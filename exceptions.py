from color import Colors as C


class Exceptions():
    def __init__(self) -> None:
        pass

    def type_checker(origin: str, param: list, check: list, strict=False):
        """
        Checks if the types of the given parameters are correct

        :param origin: The name of the function that called this function
        :type origin: str
        :param param: The parameters that should be checked
        :type param: list
        :param check: The types that the parameters should have
        :type check: list
        :param strict: If True, the types have to match exactly, if False, the types have to be subclasses of the given types, defaults to False
        :type strict: bool, optional
        """
        print(C.ok("checking" + str(param)))
        print(C.ok("cmmp" + str(check)))

        if (len(param) != len(check)):
            print(C.error("[" +
                          origin +
                          "] ERROR:" +
                          (str(len(check))) +
                          " arguments were expected but " +
                          (str(len(param))) +
                          " were given"))
            raise BaseException()

        for i in range(len(param)):

            if (((type(check[i])) == list)):
                if ((type(param[i])) == list):
                    obj = Exceptions()
                    obj.type_checker_rek(origin, param[i], check[i], strict)
                else:
                    print(C.error("[" +
                                  origin +
                                  "] ERROR: Type " +
                                  (str(type(check[i]))) +
                                  " was expected as " +
                                  (str(i)) +
                                  "-th argument but " +
                                  (str(type(param[i]))) +
                                  " was found"))
                    raise BaseException()

            elif ((not isinstance((param[i]), check[i])) and not (issubclass(type(param[i]), check[i])) and not strict):
                print(C.error("[" +
                              origin +
                              "] ERROR: Type " +
                              (str(check[i])) +
                              " was expected as " +
                              (str(i)) +
                              "-th argument but " +
                              (str(type(param[i]))) +
                              " was found"))
                raise BaseException()

            elif ((not isinstance((param[i]), check[i])) and strict):
                print(C.error("[" +
                              origin +
                              "] ERROR: Type " +
                              (str(check[i])) +
                              " was expected as " +
                              (str(i)) +
                              "-th argument but " +
                              (str(type(param[i]))) +
                              " was found"))
                raise BaseException()

        print(
            C.checkSuc(
                "[" + origin + "] SUCCESS: Type check completed successfully"))

        return

    def type_checker_rek(
            self,
            origin: str,
            param: list,
            check: list,
            strict: bool):
        # print(C.ok("checking"+str(param)))
        # print(C.ok("cmmp"+str(check)))

        if (len(param) != len(check)):
            print(C.error("[" +
                          origin +
                          "] ERROR:" +
                          (str(len(check))) +
                          " arguments were expected but " +
                          (str(len(param))) +
                          " were given"))
            raise BaseException()

        for i in range(len(param)):

            if (((type(check[i])) == list)):
                if ((type(param[i])) == list):
                    self.type_checker_rek(origin, param[i], check[i])
                else:
                    print(C.error("[" +
                                  origin +
                                  "] ERROR: Type " +
                                  (str(type(check[i]))) +
                                  " was expected as " +
                                  (str(i)) +
                                  "-th argument but " +
                                  (str(type(param[i]))) +
                                  " was found"))
                    raise BaseException()
            elif ((not isinstance((param[i]), check[i])) and not (issubclass(type(param[i]), check[i])) and not strict):
                print(C.error("[" +
                              origin +
                              "] ERROR: Type " +
                              (str(check[i])) +
                              " was expected as " +
                              (str(i)) +
                              "-th argument but " +
                              (str(type(param[i]))) +
                              " was found"))
                raise BaseException()
            elif ((not isinstance((param[i]), check[i])) and strict):
                print(C.error("[" +
                              origin +
                              "] ERROR: Type " +
                              (str(check[i])) +
                              " was expected as " +
                              (str(i)) +
                              "-th argument but " +
                              (str(type(param[i]))) +
                              " was found"))
                raise BaseException()
        return

    def bound_checker(
            origin: str,
            varname: str,
            val: float,
            lower: float,
            upper: float):
        if ((val > upper) or (val < lower)):
            print(
                C.warning(
                    "[" +
                    origin +
                    "] WARNING: The variable " +
                    varname +
                    " was expected to be in the range [" +
                    str(lower) +
                    "," +
                    str(upper) +
                    "] but was " +
                    str(val)))
        else:
            print(
                C.checkSuc(
                    "[" +
                    origin +
                    "] SUCCESS: Range check of " +
                    varname +
                    " completed successfully"))
