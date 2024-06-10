# Animate first 5 predictions for each model

def create_prediction_animation_for_models(trained_models, data, map_image_path, zoom_range, options={}):
    """
    Create an animation of the player positions and future predictions on the map for each model.

    Args:
    trained_models (dict): A dictionary of trained models
    H (int): The length of the input sequence
    T (int): The length of the target sequence
    data (dict): A dictionary of games
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
    for i, (model_name, model) in enumerate(trained_models.items()):
        H, T, _ = model_name
        X_train, X_test, y_train, y_test, _, _ = sequence_data[(H, T)]
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        options['title'] = model_name
        create_prediction_animation(
            X_test, y_pred, y_test, map_image_path, zoom_range, options)
    plt.tight_layout()


# create_prediction_animation_for_models(
#     trained_models, data, map_image_path, zoom_range, options)