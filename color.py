class Colors:
    """
    Represents a class that contains colors for the console
    """

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def error(text: str):
        """
        Returns the text in red color

        :param text: The text to color
        :type text: str
        """
        return Colors.FAIL + text + Colors.ENDC

    def warning(text: str):
        """
        Returns the text in yellow color

        :param text: The text to color
        :type text: str
        """
        return Colors.WARNING + text + Colors.ENDC

    def ok(text: str):
        """
        Returns the text in green color

        :param text: The text to color
        :type text: str
        """
        return Colors.OKGREEN + text + Colors.ENDC

    def info(text: str):
        """
        Returns the text in blue color
        
        :param text: The text to color
        :type text: str
        """
        return Colors.OKCYAN + text + Colors.ENDC
