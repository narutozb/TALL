from tools.base import ToolManager


class CustomToolManager(ToolManager):
    def __init__(self):
        super().__init__()
        self.tool_name = self.__class__.__name__


class CustomTool2Manager(ToolManager):
    def __init__(self):
        super().__init__()
        self.tool_name = self.__class__.__name__
