"""
Style transfer module for applying artistic styles to geospatial visualizations.
"""

import os
from typing import Dict, List, Optional, Tuple, Union

import geopandas as gpd
import numpy as np
from PIL import Image

# Conditional import of TensorFlow to allow use of the package without it
try:
    import tensorflow as tf
    from tensorflow.keras.applications import vgg19
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class StyleTransfer:
    """
    A class for applying artistic style transfer to geospatial visualizations.
    
    This class uses neural style transfer techniques to apply artistic styles to maps
    and geospatial data visualizations.
    
    Attributes:
        style_image: The style image to draw aesthetics from
        content_image: The content image (map) to apply the style to
        model: The style transfer model
    """
    
    # Predefined artistic styles
    PREDEFINED_STYLES = {
        "watercolor": "watercolor_landscape.jpg",
        "oil_painting": "oil_painting_landscape.jpg",
        "sketch": "pencil_sketch.jpg",
        "abstract": "abstract_geometric.jpg",
        "impressionist": "impressionist_landscape.jpg",
        "ukiyo_e": "ukiyo_e_wave.jpg",
    }
    
    def __init__(
        self,
        style_image: Optional[Union[str, np.ndarray, Image.Image]] = None,
        content_image: Optional[Union[str, np.ndarray, Image.Image]] = None,
    ):
        """
        Initialize a StyleTransfer object.
        
        Args:
            style_image: Path to style image or image array/object
            content_image: Path to content image or image array/object
            
        Raises:
            ImportError: If TensorFlow is not available for neural style transfer
        """
        if not TF_AVAILABLE:
            raise ImportError(
                "TensorFlow is required for StyleTransfer. "
                "Install it with 'pip install tensorflow'."
            )
            
        self.style_image = None
        self.content_image = None
        self.model = None
        
        if style_image is not None:
            self.load_style_image(style_image)
            
        if content_image is not None:
            self.load_content_image(content_image)
    
    @classmethod
    def get_predefined_style_path(cls, style_name: str) -> str:
        """
        Get the file path for a predefined style.
        
        Args:
            style_name: Name of the predefined style
            
        Returns:
            Path to the style image file
            
        Raises:
            ValueError: If the style name is not recognized
        """
        if style_name not in cls.PREDEFINED_STYLES:
            raise ValueError(
                f"Unknown style: {style_name}. Available styles: "
                f"{', '.join(cls.PREDEFINED_STYLES.keys())}"
            )
            
        # Get the style file from the package data directory
        import pkg_resources
        
        try:
            style_path = pkg_resources.resource_filename(
                "geo_infer_art", f"data/styles/{cls.PREDEFINED_STYLES[style_name]}"
            )
            
            # Check if the file exists
            if not os.path.exists(style_path):
                raise FileNotFoundError(f"Style file not found: {style_path}")
                
            return style_path
            
        except (pkg_resources.DistributionNotFound, FileNotFoundError):
            # Fallback to looking in a data directory relative to the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.abspath(os.path.join(current_dir, "../../../.."))
            style_path = os.path.join(
                root_dir, "data/styles", cls.PREDEFINED_STYLES[style_name]
            )
            
            if not os.path.exists(style_path):
                raise FileNotFoundError(
                    f"Style file not found for '{style_name}'. "
                    f"Expected at: {style_path}"
                )
                
            return style_path
    
    def load_style_image(self, style_image: Union[str, np.ndarray, Image.Image]) -> None:
        """
        Load the style image to use for transfer.
        
        Args:
            style_image: Path to style image, or image array/object
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
            ValueError: If the image can't be processed
        """
        if isinstance(style_image, str):
            # Check if it's a predefined style name
            if style_image in self.PREDEFINED_STYLES:
                style_path = self.get_predefined_style_path(style_image)
                self.style_image = self._load_and_preprocess_image(style_path)
            else:
                # Assume it's a file path
                self.style_image = self._load_and_preprocess_image(style_image)
        elif isinstance(style_image, np.ndarray):
            # Preprocess the numpy array
            self.style_image = self._preprocess_image_array(style_image)
        elif isinstance(style_image, Image.Image):
            # Convert PIL Image to numpy array and preprocess
            img_array = np.array(style_image)
            self.style_image = self._preprocess_image_array(img_array)
        else:
            raise ValueError(
                f"Unsupported style_image type: {type(style_image)}. "
                "Expected string path, numpy array, or PIL Image."
            )
    
    def load_content_image(self, content_image: Union[str, np.ndarray, Image.Image]) -> None:
        """
        Load the content image to apply the style to.
        
        Args:
            content_image: Path to content image, or image array/object
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
            ValueError: If the image can't be processed
        """
        if isinstance(content_image, str):
            self.content_image = self._load_and_preprocess_image(content_image)
        elif isinstance(content_image, np.ndarray):
            self.content_image = self._preprocess_image_array(content_image)
        elif isinstance(content_image, Image.Image):
            img_array = np.array(content_image)
            self.content_image = self._preprocess_image_array(img_array)
        else:
            raise ValueError(
                f"Unsupported content_image type: {type(content_image)}. "
                "Expected string path, numpy array, or PIL Image."
            )
    
    def _load_and_preprocess_image(self, image_path: str) -> tf.Tensor:
        """
        Load an image from a file and preprocess it for the VGG model.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image tensor
            
        Raises:
            FileNotFoundError: If the image file doesn't exist
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
            
        # Load and convert to RGB (in case of grayscale or RGBA)
        img = Image.open(image_path).convert('RGB')
        img = img.resize((224, 224))  # Resize for VGG
        img_array = np.array(img)
        
        return self._preprocess_image_array(img_array)
    
    def _preprocess_image_array(self, img_array: np.ndarray) -> tf.Tensor:
        """
        Preprocess a numpy image array for the VGG model.
        
        Args:
            img_array: Image as a numpy array
            
        Returns:
            Preprocessed image tensor
        """
        # Ensure the array has 3 channels (RGB)
        if img_array.ndim == 2:
            # Grayscale to RGB
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[-1] == 4:
            # RGBA to RGB (discard alpha channel)
            img_array = img_array[..., :3]
            
        # Convert to float and preprocess for VGG19
        img_tensor = tf.convert_to_tensor(img_array, dtype=tf.float32)
        img_tensor = tf.expand_dims(img_tensor, axis=0)
        
        # Preprocess using VGG19 preprocessing
        return vgg19.preprocess_input(img_tensor)
    
    def _build_model(self) -> None:
        """
        Build the style transfer model using VGG19.
        
        This method creates a model that extracts features at specified
        content and style layers from the VGG19 network.
        """
        # Content layer - where we'll get content features
        content_layers = ['block5_conv2'] 
        
        # Style layers - where we'll get style features
        style_layers = [
            'block1_conv1',
            'block2_conv1',
            'block3_conv1', 
            'block4_conv1', 
            'block5_conv1'
        ]
        
        # Load the VGG19 model without the top classification layer
        vgg = vgg19.VGG19(include_top=False, weights='imagenet')
        vgg.trainable = False
        
        # Get the outputs of the content and style layers
        style_outputs = [vgg.get_layer(name).output for name in style_layers]
        content_outputs = [vgg.get_layer(name).output for name in content_layers]
        
        # Combine them into a single model
        model_outputs = style_outputs + content_outputs
        self.model = tf.keras.Model(vgg.input, model_outputs)
    
    @staticmethod
    def apply(
        geo_data: Union[gpd.GeoDataFrame, np.ndarray],
        style: str = "watercolor",
        content_image: Optional[Union[str, np.ndarray, Image.Image]] = None,
        style_image: Optional[Union[str, np.ndarray, Image.Image]] = None,
        style_weight: float = 1e-2,
        content_weight: float = 1e4,
        iterations: int = 100,
        color_palette: Optional[str] = None,
    ) -> Image.Image:
        """
        Apply artistic style transfer to geospatial data.
        
        Args:
            geo_data: GeoDataFrame or raster data to visualize
            style: Name of the predefined style or path to style image
            content_image: Optional content image to use instead of rendering geo_data
            style_image: Optional style image to use instead of predefined style
            style_weight: Weight for style loss in the optimization
            content_weight: Weight for content loss in the optimization
            iterations: Number of optimization iterations
            color_palette: Optional color palette to apply to the result
            
        Returns:
            Stylized image as a PIL Image
            
        Raises:
            ImportError: If TensorFlow is not available
            ValueError: If both geo_data and content_image are None
        """
        # Import locally to avoid top-level TensorFlow import
        from geo_infer_art.core.visualization import GeoArt
        
        if not TF_AVAILABLE:
            raise ImportError(
                "TensorFlow is required for StyleTransfer. "
                "Install it with 'pip install tensorflow'."
            )
            
        # Create a StyleTransfer instance
        transferer = StyleTransfer()
        
        # Load the style image
        if style_image is not None:
            transferer.load_style_image(style_image)
        else:
            transferer.load_style_image(style)
            
        # Prepare content image
        if content_image is not None:
            transferer.load_content_image(content_image)
        elif geo_data is not None:
            # Render the geo_data to an image
            import io
            import matplotlib.pyplot as plt
            
            geo_art = GeoArt(data=geo_data)
            if color_palette:
                geo_art.apply_style(color_palette=color_palette)
            else:
                geo_art.apply_style()
                
            # Save figure to a buffer and load as image
            buf = io.BytesIO()
            geo_art._figure.savefig(buf, format='png', dpi=300, bbox_inches='tight')
            buf.seek(0)
            content_img = Image.open(buf)
            transferer.load_content_image(content_img)
        else:
            raise ValueError("Either geo_data or content_image must be provided")
            
        # Build the model
        transferer._build_model()
        
        # Apply neural style transfer
        stylized_image = transferer._apply_neural_style_transfer(
            style_weight=style_weight,
            content_weight=content_weight,
            iterations=iterations,
        )
        
        return stylized_image
    
    def _apply_neural_style_transfer(
        self,
        style_weight: float = 1e-2,
        content_weight: float = 1e4,
        iterations: int = 100,
    ) -> Image.Image:
        """
        Apply neural style transfer using TensorFlow.
        
        Args:
            style_weight: Weight for style loss in the optimization
            content_weight: Weight for content loss in the optimization
            iterations: Number of optimization iterations
            
        Returns:
            Stylized image as a PIL Image
            
        Raises:
            ValueError: If style or content image is not loaded
        """
        if self.style_image is None:
            raise ValueError("Style image not loaded. Call load_style_image first.")
            
        if self.content_image is None:
            raise ValueError("Content image not loaded. Call load_content_image first.")
            
        if self.model is None:
            self._build_model()
            
        # Get the feature representations of the content and style images
        style_features = self.model(self.style_image)
        content_features = self.model(self.content_image)
        
        # Split into style and content features
        num_style_layers = 5  # Defined in _build_model
        style_features = style_features[:num_style_layers]
        content_features = content_features[num_style_layers:]
        
        # Create a variable to optimize (initialize with content image)
        input_image = tf.Variable(self.content_image)
        
        # Optimizer for the image
        optimizer = tf.optimizers.Adam(learning_rate=0.02, beta_1=0.99, epsilon=1e-1)
        
        # Define the loss function
        def style_content_loss():
            # Process the input image through the model
            outputs = self.model(input_image)
            style_outputs = outputs[:num_style_layers]
            content_outputs = outputs[num_style_layers:]
            
            # Calculate style loss
            style_loss = tf.add_n([
                tf.reduce_mean((style_outputs[i] - style_features[i])**2)
                for i in range(num_style_layers)
            ])
            style_loss *= style_weight / num_style_layers
            
            # Calculate content loss
            content_loss = tf.add_n([
                tf.reduce_mean((content_outputs[i] - content_features[i])**2)
                for i in range(len(content_outputs))
            ])
            content_loss *= content_weight / len(content_outputs)
            
            # Total loss
            total_loss = style_loss + content_loss
            return total_loss
            
        # Optimization loop
        for i in range(iterations):
            with tf.GradientTape() as tape:
                loss = style_content_loss()
            
            # Get the gradients and apply them to the input image
            gradients = tape.gradient(loss, input_image)
            optimizer.apply_gradients([(gradients, input_image)])
            
            # Clip the pixel values to be between 0 and 255
            input_image.assign(tf.clip_by_value(input_image, 0.0, 255.0))
            
            if i % 10 == 0:
                print(f"Iteration {i}: Loss = {loss.numpy()}")
                
        # Convert the result back to a PIL image
        result = input_image.numpy()
        result = result.reshape(result.shape[1:])
        result = np.clip(result, 0, 255).astype('uint8')
        
        return Image.fromarray(result)
    
    def save(self, image: Image.Image, output_path: str) -> str:
        """
        Save a stylized image to a file.
        
        Args:
            image: PIL Image to save
            output_path: Path where the file should be saved
            
        Returns:
            The path to the saved file
        """
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        image.save(output_path)
        return output_path 