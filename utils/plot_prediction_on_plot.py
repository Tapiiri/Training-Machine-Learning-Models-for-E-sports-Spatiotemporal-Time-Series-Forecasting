from utils.compute_zoom_limits import compute_zoom_limits
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np


def plot_prediction_on_plot(plot, points, prediction, truth, map_image_path, zoom_range, options={}):
    """
    Plot the player positions on the map, and overlay the predicted and true future positions.

    Args:
    plot (matplotlib.pyplot): The plot to display the map on (can be a subplot or the main plot
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
    """
    if not len(prediction) > 0 or not len(truth) > 0:
        return
    # Get the options
    figsize = options.get('figsize', (10, 10))
    title = options.get('title', 'Player positions and future predictions')
    inputPointsSize = options.get('inputPointsSize', 2)
    predictionPointsSize = options.get('predictionPointsSize', 2)
    truthPointsSize = options.get('truthPointsSize', 2)
    inputPointsColor = options.get('inputPointsColor', 'blue')
    predictionPointsColor = options.get('predictionPointsColor', 'red')
    truthPointsColor = options.get('truthPointsColor', 'green')
    padding = options.get('padding', 500)

    # If plot is a subplot, clear
    if hasattr(plot, 'clear'):
        plot.clear()

    map_img = mpimg.imread(map_image_path)

    # Display image scaled to the variable
    plot.imshow(map_img, extent=[
                zoom_range[0][0], zoom_range[0][1], zoom_range[1][0], zoom_range[1][1]])

    # Overlay the player positions on the map
    for player_sequence in points:
        for i in range(1, len(player_sequence), 2):
            plot.plot(player_sequence[i], player_sequence[i-1],
                      markersize=inputPointsSize, alpha=0.6, color=inputPointsColor, marker='o')

    for player in prediction:
        plot.plot(player[1], player[0], markersize=predictionPointsSize,
                  alpha=0.6, color=predictionPointsColor, marker='o')

    for player in truth:
        plot.plot(player[1], player[0], markersize=truthPointsSize,
                  alpha=0.6, color=truthPointsColor, marker='o')

    point_sequence_as_points = np.array([(point_sequence[i-1], point_sequence[i])
                                        for point_sequence in points for i in range(1, len(point_sequence), 2)])

    all_points = np.concatenate(
        (point_sequence_as_points, prediction, truth))
    # Zoom in to the center of the points
    smallest_y = np.min(all_points[:, 0])
    largest_y = np.max(all_points[:, 0])
    smallest_x = np.min(all_points[:, 1])
    largest_x = np.max(all_points[:, 1])

    # Set the limits of the plot differently for plot and subplot
    if hasattr(plot, 'gca'):
        plot = plot.gca()

    plot.set_xlim(smallest_x - padding, largest_x + padding)
    plot.set_ylim(smallest_y - padding, largest_y + padding)
    plot.set_title(title)

    # Display the plot
    plot.set_aspect('equal')
    plot.invert_yaxis()
    plot.invert_xaxis()
    plot.axis('off')
    if not hasattr(plot, 'gca'):
        plot.show()

if __name__ == "__main__":
    map_image_path = "assets/2x_2dlevelminimap.png"

    # zoom_range = compute_zoom_limits(all_players_all_games, 0)
    # print(zoom_range)
    zoom_range = ((75, 14350), (75, 14350))

    i = slice(0, 1)
    print(y_test[i])
    plot_prediction_on_plot(
        plt, X_test[i], y_test[i], y_test[i], map_image_path, zoom_range)