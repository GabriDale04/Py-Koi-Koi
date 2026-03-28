from core import Window

def center_x(width : float) -> float:
    """
    Returns the x-coordinate required to horizontally center an object with the given width inside the window.

    Parameters
    ----------
    width
        The width of the object to center.
    """
    width = float(width)

    return (Window.width - width) / 2

def center_y(height : float) -> float:
    """
    Returns the y-coordinate required to vertically center an object with the given height inside the window.

    Parameters
    ----------
    height
        The height of the object to center.
    """
    height = float(height)

    return (Window.height - height) / 2

def center_on(container_coord : float, container_dim : float, object_dim) -> float:
    container_dim = float(container_dim)
    object_dim = float(object_dim)

    return container_coord + (container_dim - object_dim) / 2