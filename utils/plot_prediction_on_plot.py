from utils.compute_zoom_limits import compute_zoom_limits
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

def plot_prediction_on_plot(plot, points, prediction, truth, map_image_path, zoom_range, options={}):
    """
    Plot the player positions on the map, and overlay the predicted and true future positions.

    Args:
        plot (matplotlib.pyplot): The plot to display the map on (can be a subplot or the main plot)
        points (np.array): The player positions (x, y) at each time step
        prediction (np.array): The predicted future player positions (x, y)
        truth (np.array): The true future player positions (x, y)
        map_image_path (str): The path to the map image
        zoom_range (tuple): The x and y limits to zoom in to
        options (dict): Additional options for the plot
    """
    if not len(prediction) or not len(truth):
        return
    
    # Extract options with default values
    figsize = options.get('figsize', (10, 10))
    title = options.get('title', 'Player positions and future predictions')
    input_points_size = options.get('inputPointsSize', 2)
    prediction_points_size = options.get('predictionPointsSize', 2)
    truth_points_size = options.get('truthPointsSize', 2)
    input_points_color = options.get('inputPointsColor', 'blue')
    prediction_points_color = options.get('predictionPointsColor', 'red')
    truth_points_color = options.get('truthPointsColor', 'green')
    padding = options.get('padding', 0.1)

    # Clear the plot if it is a subplot
    if hasattr(plot, 'clear'):
        plot.clear()

    # Load and display the map image
    map_img = mpimg.imread(map_image_path)
    plot.imshow(map_img, extent=[zoom_range[0][0], zoom_range[0][1], zoom_range[1][0], zoom_range[1][1]])

    # Plot player positions
    def plot_positions(positions, size, color, label=False):
        for player in positions:
            plot.plot(player[1], player[0], markersize=size, alpha=0.6, color=color, marker='o')
        if label:
            plot.text(positions[-1][1], positions[-1][0], f'{label}({positions[-1][1]:.2f}, {positions[-1][0]:.2f})',
                      fontsize=8, color=color)
    
    for player_sequence in points:
        plot_positions([(player_sequence[i-1], player_sequence[i]) for i in range(1, len(player_sequence), 2)], 
                       input_points_size, input_points_color)
    
    plot_positions(prediction, prediction_points_size, prediction_points_color, 'P')
    plot_positions(truth, truth_points_size, truth_points_color, 'T')

    # Determine zoom limits
    all_points = np.vstack([(point_sequence[i-1], point_sequence[i]) for point_sequence in points for i in range(1, len(point_sequence), 2)] + [prediction, truth])
    smallest_x, largest_x = np.min(all_points[:, 1]), np.max(all_points[:, 1])
    smallest_y, largest_y = np.min(all_points[:, 0]), np.max(all_points[:, 0])

    # Set plot limits and properties
    def set_plot_properties(ax):
        ax.set_xlim(smallest_x - padding, largest_x + padding)
        ax.set_ylim(smallest_y - padding, largest_y + padding)
        ax.set_title(title)
        ax.set_aspect('equal')
        ax.invert_yaxis()
        ax.invert_xaxis()
        ax.axis('off')

    if hasattr(plot, 'gca'):
        set_plot_properties(plot.gca())
        plot.show()
    else:
        set_plot_properties(plot)
        
if __name__ == "__main__":
    map_image_path = "assets/2x_2dlevelminimap.png"
    zoom_range = ((75, 14350), (75, 14350))

    i = slice(0, 1)
    plot_prediction_on_plot(plt, X_test[i], y_test[i], y_test[i], map_image_path, zoom_range)
