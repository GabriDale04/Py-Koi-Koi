from core import Window

def center_x(width : float) -> float:
    width = float(width)

    return (Window.width - width) / 2

def center_y(height : float) -> float:
    height = float(height)

    return (Window.height - height) / 2