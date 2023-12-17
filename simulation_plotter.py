from policies import Policy
from policies import LOOKPolicy, SCANPolicy, FCFSPolicy, SSTFPolicy, PWDPPolicy, PWDPPolicyEnhanced, PWDPPolicyOptimized
from debug import Debug as DB
from parameter import Parameter, ElevatorParameter, TimeDistrParameter, PolicyParameter
from exceptions import Exceptions as EXC
from elevator import Elevator
from plotter.plotter2D import Plotter2D as P2D
from plotter.plotter3D import Plotter3D as P3D
from building import Building
from simulation import Simulation
from simulation_statistics import Objective
from progress_bar import ProgressBar
import distributions

import numpy as np
import random
import multiprocessing as mp
from datetime import datetime


class SimulationPlotter():
    def __init__(
            self,
            elevator_args=[[0, 9, [LOOKPolicy], 10]],
            distr_type=distributions.ShoppingMallDistribution,
            seed=-1,
            distr_init=None):
    
        """
        Initialises the Simulation Plotter and enables various plottings with the given input as standard parameters.

        :param elevator_args: List containing all elevator arguments. 
        :type elevator_args: list
        :param distr_type: The distribution type of the simulation.
        :type distr_type: Distribution
        :param seed: The seed for the simulation. If -1, no seed will be used.
        :type seed: int
        :param distr_init: The distribution object. If None, a new object will be created with the distribution type. If not None, it will be used directly.
        :type distr_init: Distribution, optional
        :rtype: None
        """

        self.distribution = distr_type() if (distr_init is None) else distr_init
        self.floor_amount = self.distribution.floor_amount
        self.seed = seed
        self.elevator_args = elevator_args
        self.elevators_init = []

        for i in range(len(elevator_args)):
            self.elevators_init.append([])

        self.tasks_per_thread = 4

    

    def param_plotter_2d(
            self,
            obj: list,
            param: Parameter,
            start_val,
            end_val,
            steps,
            average_of=1,
            save_plot=False,
            name="param_plotter_2d"):
        """
        Simulate the parameter param with steps amount of simulations equidistant in [start_val,end_val]
        The average_of defines how often each step stated above gets executed. The average will be taken
        to further compute any plots. The list obj contains the metrics which will be plotted and measured during
        this numerical experiment.

        :param obj: List of objectives to be plotted.
        :type obj: list
        :param param: The parameter to be simulated.
        :type param: Parameter
        :param start_val: The start value of the simulation.
        :type start_val: int
        :param end_val: The end value of the simulation.
        :type end_val: int
        :param steps: The amount of steps in the simulation.
        :type steps: int
        :param average_of: The amount of simulations objective.
        :type average_of: int, optional
        :param save_plot: Whether the plot should be saved or not.
        :type save_plot: bool, optional
        :param name: The name of the plot.
        :type name: str, optional
        :rtype: None
        """
        obj_list = obj
        objective_data = []
        objective_names = []
        objective_temp = []
        for i in range(len(obj_list)):
            objective_names.append(obj_list[i].value)
            objective_data.append([])
            objective_temp.append([])
        parameter_data = np.linspace(start_val, end_val, num=steps)
        bar = ProgressBar(len(parameter_data) * average_of, "Simulating: ")

        for i in range(len(parameter_data)):
            self._update_handler(param, parameter_data[i])
            for a in range(average_of):
                bar.update()
                simulation = self._init()
                simulation.run(days=1, time_scale=-1)
                for q in range(len(obj_list)):
                    x = (simulation.statistics.get_objective(obj_list[q]))
                    objective_temp[q].append(x)
            for q in range(len(obj_list)):
                self._del_none(objective_temp[q])
                objective_data[q].append(np.mean(objective_temp[q]))
                objective_temp[q] = []
        plt = P2D(parameter_data, param.name(), objective_data, objective_names)
        plt.plot_normal(name, save=save_plot)

    def param_plotter_3d(
            self,
            obj: Objective,
            param1: list,
            param2: list,
            average_of=1,
            save_plot=False,
            name=""):
        """
        Simulate two parameters param1 and param2 with steps amount of simulations equidistant
        in their respective [start_val,end_val] The average_of defines how often each step stated above gets executed.
        The average will be taken to further compute any plots. The obj represents the metric which will be plotted
        and measured during this numerical experiment.

        :param obj: The objective to be plotted.
        :type obj: Objective
        :param param1: The first parameter to be simulated.
        :type param1: list
        :param param2: The second parameter to be simulated.
        :type param2: list
        :param average_of: The amount of simulations per objective.
        :type average_of: int, optional
        :param save_plot: Whether the plot should be saved or not.
        :type save_plot: bool, optional
        :param name: The name of the plot.
        :type name: str, optional
        :rtype: None
        """
        objective = obj
        temp_res = []
        objective_temp = []
        par1 = param1[0]
        start_val_1 = param1[1]
        end_val_1 = param1[2]
        steps1 = param1[3]

        par2 = param2[0]
        start_val_2 = param2[1]
        end_val_2 = param2[2]
        steps2 = param2[3]

        simulations = []

        threads = mp.cpu_count()

        print_name = name if name != "" else self.distribution.distribution_name + " Scenario"
        print(f"Plotting {print_name} with {par1.name()} and {par2.name()} using {threads} threads with {self.tasks_per_thread} simulations per Thread.")

        if (name == ""):
            name = self.distribution.distribution_name + " Scenario"

        parameter_data1 = np.linspace(start_val_1, end_val_1, num=steps1)
        parameter_data2 = np.linspace(start_val_2, end_val_2, num=steps2)

        pool = mp.Pool()
        simulations = []
        results = []
        objective_data = []
        seed_store = self.seed

        for i in range(len(parameter_data2)):
            objective_data.append([])
            for j in range(len(parameter_data1)):
                objective_data[i].append([])
                self.seed = seed_store

                for k in range(len(self.elevator_args)):
                    self._update_handler(par1, parameter_data1[j], k)
                    self._update_handler(par2, parameter_data2[i], k)

                for a in range(average_of):
                    self.seed += 1234
                    simulation = self._init()
                    simulations.append((j, i, simulation))

        tasks = self._partition_tasks(simulations)

        bar = ProgressBar(len(tasks), "Simulating: ")
        bar.show()

        for i in range(len(tasks)):
            result = pool.apply_async(
                self._param_plotter_3d_worker, args=(
                    tasks[i], obj))
            results.append(result)

        temp_res = []

        for result in results:
            temp_res.append(result.get())
            bar.update()

        temp_res = self._unpartition_results(temp_res)

        pool.close()
        pool.join()

        print(f"Simulation {name} finished.")

        for i in range(len(temp_res)):
            vari = temp_res[i][0]
            varj = temp_res[i][1]
            objective_data[varj][vari].append(temp_res[i][2])

        self._extract_mean_3d(objective_data)

        plt = P3D(
            parameter_data1,
            par1.name(),
            parameter_data2,
            par2.name(),
            objective_data,
            objective.value)
        plt.plot_normal(
            name,
            show_min=True,
            show_max=True,
            save=save_plot,
            interpolation="bilinear")

    def _param_plotter_3d_worker(self, tuples, obj):
        """
        Computes a list of simulation determined by the tuples and returns a list of tuples containing the results. 
        Used for multiprocessing.

        param tuples: List of tuples containing the parameters for the simulation.
        type tuples: list
        param obj: The objective to be plotted.
        type obj: Objective
        return: List of tuples containing the results.
        rtype: list
        """
        result = []
        for tuple in tuples:
            simulation = tuple[2]
            simulation.run(days=1, time_scale=-1)
            x = (simulation.statistics.get_objective(obj))
            result.append((tuple[0], tuple[1], x))
        return result

    def param_plotter_3d_permutations(
            self,
            obj: Objective,
            from_val: int,
            to_val: int,
            steps: int,
            avg_of=1):
        """
        Plots all permutations of the parameters in PolicyParameter.

        :param obj: The objective to be plotted.
        :type obj: Objective
        :param from_val: The start value of the simulation.
        :type from_val: int
        :param to_val: The end value of the simulation.
        :type to_val: int
        :param steps: The amount of steps in the simulation.
        :type steps: int
        :param average_of: The amount of simulations per objective.
        :type average_of: int, optional
        :rtype: None
        """
        P = PolicyParameter
        parameters = [
            P.ELEV_BUT_TIME_WEIGHT,
            P.ELEV_BUT_WEIGHT,
            P.FLOOR_BUT_TIME_WEIGHT,
            P.FLOOR_BUT_WEIGHT,
            P.COMP_WEIGHT,
            P.DIST_EXPONENT,
            P.DIST_WEIGHT]
        tot = len(parameters) * (len(parameters) - 1) // 2
        iter = 1
        current_time = datetime.now().strftime("%H_%M_%S")
        distr_name_without_spaces = self.distribution.distribution_name.replace(
            " ", "-")

        print("Starting to plot all parameter permutations.")

        for i, p1 in enumerate(parameters):
            for j, p2 in enumerate(parameters):
                if (j >= i):
                    continue
                name = f"{p1.short_name()}-vs-{p2.short_name()}-{distr_name_without_spaces}-{current_time}"
                print(f"PLOTTING {iter}/{tot}: {name}")
                self.param_plotter_3d(
                    obj, [
                        p1, from_val, to_val, steps], [
                        p2, from_val, to_val, steps], avg_of, save_plot=True, name=name)
                iter += 1

        print(f"Finished plotting {tot} permutations.")

    def distr_plotter_2d(
            self,
            distr,
            target=False,
            save_plot=False,
            name="",
            combine_floors=None,
            plot_time=0):
        """
        Plots the distribution of the simulation. The target parameter specifies whether the target or spawn distribution should be plotted.
        Combine floors specifies which floors should be combined, input a list of indices tuples of ranges.
        If None, all floors will be plotted individually.

        If plot_time=0, only the floor distribution will be plotted.
        If plot_time=1, only the time distribution will be plotted.
        If plot_time=2, both will be plotted.

        :param distr: The distribution to be plotted.
        :type distr: Distribution
        :param target: Whether the target or spawn distribution should be plotted.
        :type target: bool, optional
        :param save_plot: Whether the plot should be saved or not.
        :type save_plot: bool, optional
        :param name: The name of the plot.
        :type name: str, optional
        :param combine_floors: List of tuples of indices of floors to be combined.
        :type combine_floors: list, optional
        :param plot_time: Specifies the starting time of the distribution.
        :type plot_time: int, optional
        :rtype: None
        """
        distr_init = distr()
        start = 0
        end = distr_init.max_time
        key_frames = list(range(start, end + 1))
        floor_amount = self.floor_amount

        if (combine_floors is None):
            combine_floors = [(i, i) for i in range(floor_amount)]

        if (name == ""):
            name = self.distribution.distribution_name + " Scenario"

        curve_names = []
        floor_target_data = []
        floor_spawn_data = []

        for i in range(floor_amount):
            floor_target_data.append([])
            floor_spawn_data.append([])

        if plot_time == 0 or plot_time == 2:
            for below, above in combine_floors:
                if below != above:
                    curve_names.append(f"Floor {below}-{above}")
                else:
                    curve_names.append(f"Floor {below}")

        time_data = []

        for t in range(len(key_frames)):
            floorSpawnDistribution, floorTargetDistribution = distr_init.get_floor_distributions(
                t)
            passenger_distr_at_time = distr_init.passenger_distribution.get_interpolated_prob(
                t)
            time_data.append(passenger_distr_at_time)

            for i in range(floor_amount):
                if (plot_time == 0):
                    floor_target_data[i].append(
                        floorTargetDistribution.distribution[i])
                    floor_spawn_data[i].append(
                        floorSpawnDistribution.distribution[i])
                else:
                    floor_target_data[i].append(
                        floorTargetDistribution.distribution[i] *
                        passenger_distr_at_time)
                    floor_spawn_data[i].append(
                        floorSpawnDistribution.distribution[i] *
                        passenger_distr_at_time)

        # Convert to hours
        key_frames = [x / 3600 for x in key_frames]

        # Combine floors
        combined_floor_target_data = []
        combined_floor_spawn_data = []

        for i, _ in combine_floors:
            combined_floor_target_data.append(floor_target_data[i])
            combined_floor_spawn_data.append(floor_spawn_data[i])

        if plot_time == 1:
            # Plot only time distribution
            plt = P2D(
                key_frames,
                "time [h]",
                [time_data],
                ["Spawn Rate Factor"],
                y_label="Spawn Rate Factor")
        elif target:
            plt = P2D(
                key_frames,
                "time [h]",
                combined_floor_target_data,
                curve_names,
                y_label="Floor Selection Weight")
        else:
            plt = P2D(
                key_frames,
                "time [h]",
                combined_floor_spawn_data,
                curve_names,
                y_label="Floor Selection Weight")
        plt.plot_normal(name, cmap="winter", save=save_plot, max_val=24)

    def policy_plotter_2d(
            self,
            objective: Objective,
            policies: list,
            time_scale="h",
            average_of=1,
            save_plot=False,
            name=""):
        """
        Plots the given objective as benchmark over all given policies. The time_scale specifies how often 
        the objective should be measured. The average_of specifies how often the simulation should be run
        
        :param objective: The objective to be plotted.
        :type objective: Objective
        :param policies: The policies to be compared.
        :type policies: list
        :param time_scale: The time scale of the objective.
        :type time_scale: str, optional
        :param average_of: The amount of simulations per objective.
        :type average_of: int, optional
        :param save_plot: Whether the plot should be saved or not.
        :type save_plot: bool, optional
        :param name: The name of the plot.
        :type name: str, optional
        :rtype: None
        """

        bar = ProgressBar(len(policies) * average_of, "Simulating: ")
        objective_data = []
        objective_temp = []
        objective_names = []
        objective_average = []

        policy_average_end_result = []

        t = 1
        if (time_scale == "h"):
            t = 60 * 60
        elif (time_scale == "m"):
            t = 60

        if (name == ""):
            name = self.distribution.distribution_name + " Scenario"

        distr = self.distribution
        start = 0
        end = (distr.max_time) // t
        seed_store = self.seed

        key_frames = list(range(start, end))

        for i in range(len(policies)):
            policy_end_result = []
            self.seed = seed_store
            objective_names.append(policies[i]().name())
            for j in range(len(self.elevator_args)):
                self._update_handler(PolicyParameter.POLICY, policies[i], j)
            for a in range(average_of):
                self.seed += 1234
                bar.update()
                simulation = self._init()
                simulation.run(days=1, time_scale=-1)
                x = (
                    simulation.statistics.get_objective(
                        objective, t, 24 * 60 * 60 // t))
                objective_temp.append(x)
                y = (simulation.statistics.get_objective(objective))
                policy_end_result.append(y)
            objective_data.append(self._extract_mean(objective_temp))
            objective_temp = []
            policy_average_end_result.append(np.mean(policy_end_result))
        for i in range(len(policies)):
            print(
                f"Policy {policies[i]().name()} has an average of {policy_average_end_result[i]} {objective.value} at the end of the simulation")
        plt = P2D(
            key_frames,
            "Time [" + str(time_scale) + "]",
            objective_data,
            objective_names,
            y_label=objective.value)
        plt.plot_normal(name, save=save_plot)

    def policy_plotter_2d_scenarios(
            self,
            objective: Objective,
            policy,
            scenarios,
            scenario_names,
            time_scale="h",
            average_of=1,
            save_plot=False,
            name=""):
        """
        Compares the given policy over all given scenarios. The time_scale specifies how often 
        the objective should be measured. The average_of specifies how often the simulation should be run

        :param objective: The objective to be plotted.
        :type objective: Objective
        :param policy: The policy to be compared.
        :type policy: Policy
        :param scenarios: The scenarios to be compared.
        :type scenarios: list
        :param scenario_names: The names of the scenarios.
        :type scenario_names: list
        :param time_scale: The time scale of the objective.
        :type time_scale: str, optional
        :param average_of: The amount of simulations per objective.
        :type average_of: int, optional
        :param save_plot: Whether the plot should be saved or not.
        :type save_plot: bool, optional
        :param name: The name of the plot.
        :type name: str, optional
        :rtype: None
        """
        
        bar = ProgressBar(len(scenarios) * average_of, "Simulating: ")
        self._update_handler(PolicyParameter.POLICY, policy)
        objective_data = []
        objective_temp = []
        objective_names = []
        objective_average = []

        policy_average_end_result = []

        t = 1
        if (time_scale == "h"):
            t = 60 * 60
        elif (time_scale == "m"):
            t = 60

        if (name == ""):
            name = "Different Scenarios"

        distr = self.distribution
        start = 0
        end = (distr.max_time) // t
        seed_store = self.seed

        key_frames = list(range(start, end))

        for i in range(len(scenarios)):
            self.distribution = scenarios[i]()
            policy_end_result = []
            self.seed = seed_store
            objective_names.append(scenario_names[i])
            for a in range(average_of):
                self.seed += 1234
                bar.update()
                simulation = self._init()
                simulation.run(days=1, time_scale=-1)
                x = (
                    simulation.statistics.get_objective(
                        objective, t, 24 * 60 * 60 // t))
                objective_temp.append(x)
                y = (simulation.statistics.get_objective(objective))
                policy_end_result.append(y)
            objective_data.append(self._extract_mean(objective_temp))
            objective_temp = []
            policy_average_end_result.append(np.mean(policy_end_result))
        plt = P2D(
            key_frames,
            "time [" + str(time_scale) + "]",
            objective_data,
            objective_names,
            y_label=objective.value)
        plt.plot_normal(name, cmap="winter", save=save_plot)


    

    def _partition_tasks(self, input: list):
        """
        Given a list of tasks, this function partitions the tasks into a list of lists, where each list adheres to the tasks_per_thread parameter.
        It returns a list of lists, where each list contains the tasks for a single thread. Used for multiprocessing.

        :param input: The list of tasks to be partitioned.
        :type input: list
        :return: The partitioned tasks.
        :rtype: list
        """

        tasks = [[]]
        current_thread = 0
        current_amount = 0
        while (len(input) > 0):
            if (current_amount >= self.tasks_per_thread):
                current_amount = 0
                current_thread += 1
                tasks.append([])
            else:
                tasks[current_thread].append(input.pop())
                current_amount += 1
        return tasks

    def _unpartition_results(self, input: list):
        """
        Given a list of lists of results, this function unpartitions the results into a single list. Used for multiprocessing.

        :param input: The list of lists of results to be unpartitioned.
        :type input: list
        :return: The unpartitioned results.
        :rtype: list
        """
        out = []
        for x in range(len(input)):
            for y in range(len(input[x])):
                out.append(input[x][y])
        return out

    def _extract_mean(self, input: list):
        """
        Extracts the mean of the columns of a matrix represented by input.
        Individual None values get deleted in a column. When column only consists of
        None, average will be marked with -1, such that we can handle that case later.

        :param input: The matrix to be averaged.
        :type input: list
        :return: The averaged matrix.
        :rtype: list
        """
        if (len(input) == 0 or input is None):
            raise BaseException("List cannot be empty or of length 0")

        avg = []
        avg_temp = []

        x_len = len(input)
        y_len = len(input[0])

        for y in range(y_len):
            for x in range(x_len):
                avg_temp.append(input[x][y])
            self._del_none(avg_temp)
            if (len(avg_temp) == 0):
                avg_temp.append(-1)
            avg.append(np.mean(avg_temp))
            avg_temp = []
        return avg

    def _extract_mean_3d(self, input: list):
        """
        Extracts the mean of the columns of a 3d matrix represented by input.
        Individual None values get deleted in a column.

        :param input: The matrix to be averaged.
        :type input: list
        :return: The averaged matrix.
        :rtype: list
        """
        if (len(input) == 0 or input is None):
            raise BaseException("List cannot be empty or of length 0")

        for x in range(len(input)):
            for y in range(len(input[x])):
                avg_temp = []
                for c in range(len(input[x][y])):
                    avg_temp.append(input[x][y])
                self._del_none(avg_temp)
                if (len(avg_temp) == 0):
                    avg_temp.append(-1)
                input[x][y] = np.mean(avg_temp)

    def _init(self):
        """
        Initialises an simulation with the current member variables as arguments.
        The arguments are:
        - elevator_args      : stores the arguments of the i-th elevator in elevator_args[i]
        - distr_type         : stores the scenario [ShoppingMallDistribution, RooftopBarDistribution, ResidentialBuildingDistribution]
        - self.distribution  : stores the distribution
        - self.floor_amount  : stores the floor amount

        :return: The initialised simulation.
        :rtype: Simulation
        """
        if (self.seed != -1):
            random.seed(self.seed)
            np.random.seed(self.seed)
        elevators = []
        for i in range(len(self.elevator_args)):
            self._init_policy(i)
            elevators.append(
                Elevator(
                    self.elevator_args[i][0],
                    self.elevator_args[i][1],
                    self.elevators_init[i],
                    self.elevator_args[i][3]))

        building = Building(elevators, self.floor_amount, self.distribution)
        return Simulation(building, self.seed)

    def _init_policy(self, i):
        """
        Initialises the policy of the i-th elevator in elevator_args[i].

        :param i: The index of the elevator.
        :type i: int
        :rtype: None
        """
        t = self.elevator_args[i][2][0]

        if (t == LOOKPolicy):
            self.elevators_init[i] = LOOKPolicy()
        elif (t == FCFSPolicy):
            self.elevators_init[i] = FCFSPolicy()
        elif (t == SSTFPolicy):
            self.elevators_init[i] = SSTFPolicy()
        elif (t == SCANPolicy):
            self.elevators_init[i] = SCANPolicy()
        elif (t == PWDPPolicy):
            args = self.elevator_args[i][2][1:]
            self.elevators_init[i] = PWDPPolicy(*args)
        elif (t == PWDPPolicyEnhanced):
            args = self.elevator_args[i][2][1:]
            self.elevators_init[i] = PWDPPolicyEnhanced(*args)
        elif (t == PWDPPolicyOptimized):
            args = self.elevator_args[i][2][1:]
            self.elevators_init[i] = PWDPPolicyOptimized(*args)

    def _set_floor_amount(self, amount: int):
        """
        Sets the floor amount to the given amount and updates all member variables accordingly.

        :param amount: The new floor amount.
        :type amount: int
        :rtype: None
        """
        self.floor_amount = amount
        self.spawn_distr_args[0] = amount
        self.time_distr_args[0] = amount

        for i in range(len(self.elevator_args)):
            self.elevator_args[i][1] = amount - 1

    def _update_handler(self, param, new_val, index=0):
        """
        Updates the member variables according to the given parameter and value.
        If the parameter is a PolicyParameter, the value will be added to the policy list of the i-th elevator in elevator_args[i].

        :param param: The parameter to be updated.
        :type param: Parameter
        :param new_val: The new value.
        :type new_val: int
        :param index: The index of the elevator.
        :type index: int, optional
        :rtype: None
        """

        match param.case():
            case 0:
                self._update_param(param, new_val)
            case 1:
                self._update_elevator(param, new_val, index)
            case 2:
                self._update_policy(param, new_val, index)
            case 3:
                self._update_timeDistr(param, new_val)

    def _update_param(self, param, new_val):
        """
        If the to be updated parameter is a spawn-, target distribution or floor amount, the member variables will be updated accordingly.

        :param param: The parameter to be updated.
        :type param: Parameter
        :param new_val: The new value.
        :type new_val: int
        :rtype: None
        """

        match param.value:
            case 1:
                self._set_floor_amount(new_val)
            case 2:
                self.spawn_distr_args[1] = new_val
            case 3:
                self.target_distr_args[1] = new_val

    def _update_policy(self, param, new_val, index: int):
        """
        If the to be updated parameter is a PolicyParameter, the member variables will be updated accordingly.

        :param param: The parameter to be updated.
        :type param: Parameter
        :param new_val: The new value.
        :type new_val: int
        :param index: The index of the elevator.
        :type index: int
        :rtype: None
        """

        if (param.value == -1):
            self.elevator_args[index][2] = [new_val]
        else:
            self.elevator_args[index][2][param.value] = new_val

    def _add_elevator(self, args: list):
        """
        Adds an elevator with the given args to the current building

        :param args: The arguments of the elevator.
        :type args: list
        :rtype: None
        """

        self.elevator_args.append(args)
        self.elevator_args.append(None)

    def _update_elevator(self, param: ElevatorParameter, new_val, index: int):
        """
        If the to be updated parameter is an ElevatorParameter, the member variables will be updated accordingly.

        :param param: The parameter to be updated.
        :type param: Parameter
        :param new_val: The new value.
        :type new_val: int
        :param index: The index of the elevator.
        :type index: int
        :rtype: None
        """
        self.elevator_args[index][param.value] = new_val

    def _update_distr(self, distribution):
        """
        Updates the distribution to the given distribution and updates all member variables accordingly.

        :param distribution: The new distribution.
        :type distribution: Distribution
        :rtype: None
        """
        self.distribution = distribution()
        self.floor_amount = self.distribution.floor_amount

    def _update_timeDistr(self, param: TimeDistrParameter, new_val):
        """
        If the to be updated parameter is a TimeDistrParameter, the member variables will be updated accordingly.

        :param param: The parameter to be updated.
        :type param: Parameter
        :param new_val: The new value.
        :type new_val: int
        :rtype: None
        """

        if (param.value == 3):
            self.time_distr_args[param.value].append(new_val)
        else:
            self.time_distr_args[param.value] = new_val

    def _print_args(self):
        """
        Prints all member variables.

        :rtype: None
        """
        print("printing args -----")
        print(self.elevator_args)
        print(self.floor_amount)
        print(self.spawn_distr_args)
        print(self.target_distr_args)
        print(self.time_distr_args)

    def _del_none(self, lst: list):
        """
        Deletes all None values in the given list, accessed as a pointer.

        :param lst: The list to be cleaned.
        :type lst: list
        :rtype: None
        """
        for i in sorted(range(len(lst)), reverse=True):
            if (lst[i] is None):
                lst.pop(i)

    def _gen_tuple(self, param: Parameter):
        """
        Generates a tuple of all parameters except the given parameter.

        :param param: The parameter to be excluded.
        :type param: Parameter
        :return: The list of all tuple of parameters except the given parameter.
        :rtype: list
        """

        P = PolicyParameter
        parameters = [
            P.ELEV_BUT_TIME_WEIGHT,
            P.ELEV_BUT_WEIGHT,
            P.FLOOR_BUT_TIME_WEIGHT,
            P.FLOOR_BUT_WEIGHT,
            P.COMP_WEIGHT,
            P.DIST_EXPONENT,
            P.DIST_WEIGHT]

        out = []
        for i in parameters:
            if (i != param):
                out.append((param, i))
        return out


## --- START OF SCENARIO SETTINGS --- ##
# MAIN SCENARIO SETTINGS

# Choose a seed
seed = 1

# Choose whether to use a standard scenario or a custom scenario
is_custom_scenario = False

# Select from one of the three standard scenarios (ShoppingMall, Rooftop,
# Residential)
distribution = distributions.ShoppingMallDistribution

# Choose a policy for the elevators (might be overwritten by function
# parameters used later)
policy = PWDPPolicy

# Choose policy parameters (might be overwritten by function parameters
# used later)
policy_parameters = [0,0,0,0,0,0,0]

# CUSTOM SCENARIO SETTINGS
# Specify floor amount if using a CUSTOM scenario
floor_amount = 10

# Specify elevator list if using a CUSTOM scenario
elevator_capacity = 10
elevator_args = [[0, floor_amount - 1,
                 [policy, 1, 1, 1, 1, 1, 1, 1], elevator_capacity]]

## --- END OF SCENARIO SETTINGS --- ##
if __name__ == "__main__":

    if (not is_custom_scenario):
        elevator_args = []
        # Initilaize distribution to get parameters
        dist = distribution()
        # Standard scenario, set parameters automatically
        floor_amount = dist.floor_amount
        amount_of_elevators = dist.amount_of_elevators
        for i in range(amount_of_elevators):
            elevator_args.append(
                [0, floor_amount - 1, [policy, *policy_parameters], dist.elevator_capacity])
    plt = SimulationPlotter(
        elevator_args=elevator_args,
        distr_type=distribution,
        seed=seed,
        distr_init=dist)

    ## --- START OF PLOTTER SETTINGS --- ##

    # IMPORTANT: Keep indentiation of the following lines
    # Call the plotter functions here

    # Policy Comparison
    # plt.policy_plotter_2d(Objective.AWT,[SCANPolicy, FCFSPolicy, PWDPPolicy, LOOKPolicy],average_of=10, save_plot=False)
    
    # Space/Time Distribution
    # plt.distr_plotter_2d(distribution, save_plot=False, target=False, plot_time=0, combine_floors=[(0,0),(1,9)])

    # Policy Parameter Comparison
    # plt.param_plotter_3d(Objective.ATTD,[PolicyParameter.ELEV_BUT_WEIGHT,1,6,5],[PolicyParameter.FLOOR_BUT_WEIGHT,1,6,5],2,save_plot=True)

    # Policy Parameter Permutation Comparison
    # plt.param_plotter_3d_permutations(Objective.AWT, 0, 10, 20, avg_of=5)

    cool = Objective.AWT
    plt.policy_plotter_2d_scenarios(
    cool,
    SCANPolicy,
    [distributions.ResidentialBuildingDistribution, distributions.RooftopBarDistribution, distributions.ShoppingMallDistribution],
    ["Residential Building ","Rooftop Bar","Shopping Mal"],
    average_of=10,
    name = "i",
    save_plot=False
    )

    plt.policy_plotter_2d_scenarios(
    cool,
    LOOKPolicy,
    [distributions.ResidentialBuildingDistribution, distributions.RooftopBarDistribution, distributions.ShoppingMallDistribution],
    ["Residential Building ","Rooftop Bar","Shopping Mal"],
    average_of=10,
    name = "i",
    save_plot=False
    )

    plt.policy_plotter_2d_scenarios(
    cool,
    FCFSPolicy,
    [distributions.ResidentialBuildingDistribution, distributions.RooftopBarDistribution, distributions.ShoppingMallDistribution],
    ["Residential Building ","Rooftop Bar","Shopping Mal"],
    average_of=10,
    name = "i",
    save_plot=False
    )

    plt.policy_plotter_2d_scenarios(
    cool,
    SSTFPolicy,
    [distributions.ResidentialBuildingDistribution, distributions.RooftopBarDistribution, distributions.ShoppingMallDistribution],
    ["Residential Building ","Rooftop Bar","Shopping Mal"],
    average_of=10,
    name = "i",
    save_plot=False
    )


    # Multiple Policy Parameter Comparison
    run_multiple = False
    from_val, to_val, steps = 1, 11, 10
    avg_of = 1

    parameters = [
        (PolicyParameter.ELEV_BUT_WEIGHT, PolicyParameter.FLOOR_BUT_WEIGHT),
        (PolicyParameter.ELEV_BUT_WEIGHT, PolicyParameter.ELEV_BUT_TIME_WEIGHT),
        (PolicyParameter.COMP_WEIGHT, PolicyParameter.COMP_WEIGHT),
        (PolicyParameter.FLOOR_BUT_TIME_WEIGHT, PolicyParameter.FLOOR_BUT_WEIGHT),
    ]
    if run_multiple:
        for p1, p2 in parameters:
            plt.param_plotter_3d(
                Objective.AWT, [
                    p1, from_val, to_val, steps], [
                    p2, from_val, to_val, steps], avg_of, save_plot=True)

    ## --- END OF PLOTTER SETTINGS --- ##
    ## test ##