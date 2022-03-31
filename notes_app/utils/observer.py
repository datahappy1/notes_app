class Observer:
    """Abstract superclass for all observers."""

    def notify_model_is_changed(self):
        """
        The method that will be called on the observer when the model changes.
        """
