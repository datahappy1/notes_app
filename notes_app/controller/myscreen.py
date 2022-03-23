from notes_app.view.myscreen import MyScreenView


class MyScreenController:
    """
    The `MyScreenController` class represents a controller implementation.
    Coordinates work of the view with the model.

    The controller implements the strategy pattern. The controller connects to
    the view to control its actions.
    """

    def __init__(self, model):
        """
        The constructor takes a reference to the model.
        The constructor creates the view.
        """
        self.model = model
        self.view = MyScreenView(controller=self, model=self.model)

    # def on_startup(self):
    #     self.view.MainWindow.on_startup(self.model)

    def get_screen(self):
        """The method creates get the view."""
        return self.view.MainWindow(model=self.model)
