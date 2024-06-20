# Show the first 5 predictions in an animation
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
import matplotlib.pyplot as plt
from utils.plot_prediction_on_plot import plot_prediction_on_plot


def create_prediction_animation(points, prediction, truth, map_image_path, zoom_range, options={}):
    """
    Create an animation of the player positions and future predictions on the map.

    Args:
    points (np.array): The player positions (x, y) at each time step
    prediction (np.array): The predicted future player positions (x, y)
    truth (np.array): The true future player positions (x, y)
    map_image_path (str): The path to the map image
    zoom_range (tuple): The x and y limits to zoom in to
    options (dict): Additional options for the plot:
        - figsize (tuple): The size of the plot
        - title (str): The title of the plot
        - inputPointsSize (int[]): Array of sizes for the input points
        - predictionPointsSize (int[]): Array of sizes for the prediction points
        - truthPointsSize (int[]): Array of sizes for the truth points
        - inputPointsColor (str[]): Array of colors for the input points
        - predictionPointsColor (str[]): Array of colors for the prediction points
        - truthPointsColor (str[]): Array of colors for the truth points
        - padding (int): The padding to add to the zoom range
        - speed (int): The speed of the animation
    """
    fig, ax = plt.subplots()

    def update(frame):
        i = slice(frame, frame+1)
        ax.clear()
        plot_prediction_on_plot(
            ax, points[i], prediction[i], truth[i], map_image_path, zoom_range, options)
    # Variable to control animation speed
    speed = options.get('speed', 1000)

    ani = FuncAnimation(fig, update, frames=range(
        len(points)), interval=speed, blit=False)
    return HTML(ani.to_jshtml())
