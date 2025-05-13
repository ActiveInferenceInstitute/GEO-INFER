"""
ProceduralArt module for creating procedural and algorithmic art from geospatial data.
"""

import os
from typing import Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from geo_infer_art.core.aesthetics import ColorPalette


class ProceduralArt:
    """
    A class for creating procedural and algorithmic art from geospatial data.
    
    The ProceduralArt class provides methods for generating art through 
    rule-based algorithms that can be seeded with geospatial parameters.
    
    Attributes:
        params: Parameters controlling the procedural generation
        image: The generated image as a numpy array
    """
    
    # Available procedural algorithms
    ALGORITHMS = [
        "l_system",
        "cellular_automata",
        "reaction_diffusion",
        "noise_field",
        "voronoi",
        "fractal_tree"
    ]
    
    def __init__(
        self,
        algorithm: str = "noise_field",
        params: Optional[Dict] = None,
        resolution: Tuple[int, int] = (800, 800),
    ):
        """
        Initialize a ProceduralArt object.
        
        Args:
            algorithm: Name of the procedural algorithm to use
            params: Parameters for the algorithm
            resolution: Output image resolution (width, height)
            
        Raises:
            ValueError: If the algorithm is not supported
        """
        if algorithm not in self.ALGORITHMS:
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. Supported algorithms: "
                f"{', '.join(self.ALGORITHMS)}"
            )
            
        self.algorithm = algorithm
        self.params = params or {}
        self.resolution = resolution
        self.image = None
        self._figure = None
        
    @classmethod
    def from_geo_coordinates(
        cls,
        lat: float,
        lon: float,
        algorithm: str = "noise_field",
        additional_params: Optional[Dict] = None,
    ) -> 'ProceduralArt':
        """
        Create procedural art seeded by geographic coordinates.
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            algorithm: Name of the procedural algorithm to use
            additional_params: Additional parameters for the algorithm
            
        Returns:
            A new ProceduralArt object with generated art
            
        Raises:
            ValueError: If coordinates are out of range
        """
        # Validate coordinates
        if not -90 <= lat <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
            
        if not -180 <= lon <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
            
        # Initialize parameters with geo-coordinates
        params = additional_params or {}
        
        # Use coordinates to seed parameters
        # Normalize to 0-1 range
        norm_lat = (lat + 90) / 180  
        norm_lon = (lon + 180) / 360
        
        # Base parameters from coordinates
        params.update({
            "seed": int((norm_lat * 1000) + (norm_lon * 10000)),
            "x_influence": norm_lon,
            "y_influence": norm_lat,
            "geo_coordinates": (lat, lon),
        })
        
        # Create the object
        art = cls(algorithm=algorithm, params=params)
        
        # Generate the art
        art.generate()
        
        return art
    
    @classmethod
    def from_geo_features(
        cls,
        feature_type: str,
        feature_count: int,
        algorithm: str = "l_system",
        additional_params: Optional[Dict] = None,
    ) -> 'ProceduralArt':
        """
        Create procedural art based on geographic feature statistics.
        
        Args:
            feature_type: Type of geographic feature ("rivers", "mountains", "coastlines", etc.)
            feature_count: Number of features to simulate
            algorithm: Name of the procedural algorithm to use
            additional_params: Additional parameters for the algorithm
            
        Returns:
            A new ProceduralArt object with generated art
            
        Raises:
            ValueError: If the feature type is invalid
        """
        # Validate feature type
        valid_features = ["rivers", "mountains", "coastlines", "urban", "forest"]
        if feature_type not in valid_features:
            raise ValueError(
                f"Invalid feature type: {feature_type}. Valid types: "
                f"{', '.join(valid_features)}"
            )
            
        # Initialize parameters
        params = additional_params or {}
        
        # Set parameters based on feature type
        if feature_type == "rivers":
            params.update({
                "branching_factor": 0.7,
                "curvature": 0.3,
                "iteration_depth": min(feature_count, 10),
                "color_palette": "blue",
            })
            if algorithm == "noise_field":
                algorithm = "l_system"  # Override with better algorithm for rivers
                
        elif feature_type == "mountains":
            params.update({
                "roughness": 0.8,
                "peaks": min(feature_count, 30),
                "elevation_scale": 10 + min(feature_count, 20),
                "color_palette": "earth",
            })
            if algorithm == "l_system":
                algorithm = "noise_field"  # Better for mountains
                
        elif feature_type == "coastlines":
            params.update({
                "fractal_dimension": 1.2,
                "jaggedness": 0.6,
                "water_level": 0.5,
                "color_palette": "ocean",
            })
            
        elif feature_type == "urban":
            params.update({
                "grid_size": max(10, min(feature_count // 10, 50)),
                "density": min(feature_count / 100, 0.8),
                "regularity": 0.7,
                "color_palette": "grayscale",
            })
            if algorithm not in ["cellular_automata", "voronoi"]:
                algorithm = "cellular_automata"  # Better for urban
                
        elif feature_type == "forest":
            params.update({
                "tree_count": feature_count,
                "clustering": 0.6,
                "variation": 0.3,
                "color_palette": "forest",
            })
            if algorithm not in ["fractal_tree", "noise_field"]:
                algorithm = "fractal_tree"  # Better for forests
        
        # Add feature info to params
        params["feature_type"] = feature_type
        params["feature_count"] = feature_count
        
        # Create the object
        art = cls(algorithm=algorithm, params=params)
        
        # Generate the art
        art.generate()
        
        return art
    
    def generate(self) -> None:
        """
        Generate the procedural art based on the selected algorithm and parameters.
        """
        # Set random seed if provided
        if "seed" in self.params:
            np.random.seed(self.params["seed"])
            
        # Call the appropriate generation method
        if self.algorithm == "l_system":
            self._generate_l_system()
        elif self.algorithm == "cellular_automata":
            self._generate_cellular_automata()
        elif self.algorithm == "reaction_diffusion":
            self._generate_reaction_diffusion()
        elif self.algorithm == "noise_field":
            self._generate_noise_field()
        elif self.algorithm == "voronoi":
            self._generate_voronoi()
        elif self.algorithm == "fractal_tree":
            self._generate_fractal_tree()
            
        return self
    
    def _generate_noise_field(self) -> None:
        """
        Generate art using a noise field algorithm (Perlin, Simplex, etc.).
        """
        # Get parameters with defaults
        width, height = self.resolution
        noise_type = self.params.get("noise_type", "perlin")
        octaves = self.params.get("octaves", 6)
        persistence = self.params.get("persistence", 0.5)
        lacunarity = self.params.get("lacunarity", 2.0)
        scale = self.params.get("scale", 100.0)
        
        # X and Y influence can be seeded by geo coordinates
        x_influence = self.params.get("x_influence", 1.0)
        y_influence = self.params.get("y_influence", 1.0)
        
        # Create the noise field
        result = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Simplified Perlin-like noise for demonstration
        # In production code, you'd use a proper noise library
        x = np.linspace(0, scale * x_influence, width)
        y = np.linspace(0, scale * y_influence, height)
        X, Y = np.meshgrid(x, y)
        
        # Generate multi-octave noise
        noise = np.zeros((height, width))
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        for i in range(octaves):
            noise += amplitude * np.sin(X * frequency * 0.1) * np.cos(Y * frequency * 0.1)
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
            
        # Normalize noise to 0-1
        noise = (noise + max_value) / (2 * max_value)
        
        # Get color palette
        palette_name = self.params.get("color_palette", "viridis")
        palette = ColorPalette.get_palette(palette_name)
        
        # Create a figure
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        
        # Plot the noise field with the color palette
        img = ax.imshow(
            noise,
            cmap=palette.cmap,
            interpolation='bicubic',
            aspect='auto',
            extent=[0, width, 0, height],
        )
        
        # Remove axes for artistic effect
        ax.set_axis_off()
        plt.tight_layout(pad=0)
        
        # Store the figure
        self._figure = fig
        
        # Convert figure to image
        self._figure_to_image()
        
    def _generate_voronoi(self) -> None:
        """
        Generate art using Voronoi diagrams.
        """
        from scipy.spatial import Voronoi, voronoi_plot_2d
        
        # Get parameters with defaults
        width, height = self.resolution
        num_points = self.params.get("num_points", 50)
        point_clustering = self.params.get("point_clustering", 0.0)  # 0.0-1.0
        edge_width = self.params.get("edge_width", 1.0)
        
        # Generate points
        # If clustering is 0, points are uniform random
        # If clustering is 1, points are clustered around centers
        if point_clustering < 0.1:
            # Uniform random points
            points = np.random.rand(num_points, 2)
            points[:, 0] *= width
            points[:, 1] *= height
        else:
            # Create clustered points
            num_clusters = max(1, int(num_points / 10))
            cluster_centers = np.random.rand(num_clusters, 2)
            cluster_centers[:, 0] *= width
            cluster_centers[:, 1] *= height
            
            points = np.zeros((num_points, 2))
            for i in range(num_points):
                # Pick a random cluster center
                center_idx = np.random.randint(0, num_clusters)
                center = cluster_centers[center_idx]
                
                # Generate point with distance based on clustering parameter
                distance = np.random.normal(0, width/10 * (1 - point_clustering))
                angle = np.random.uniform(0, 2 * np.pi)
                
                # Calculate the offset from center
                dx = distance * np.cos(angle)
                dy = distance * np.sin(angle)
                
                # Ensure point is within bounds
                x = np.clip(center[0] + dx, 0, width)
                y = np.clip(center[1] + dy, 0, height)
                
                points[i] = [x, y]
                
        # Add corner points to ensure the diagram covers the full image
        corner_points = np.array([
            [-width, -height],
            [-width, 2*height],
            [2*width, -height],
            [2*width, 2*height],
        ])
        points = np.vstack([points, corner_points])
        
        # Create Voronoi diagram
        vor = Voronoi(points)
        
        # Get color palette
        palette_name = self.params.get("color_palette", "pastel")
        palette = ColorPalette.get_palette(palette_name)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        
        # Plot Voronoi regions with colors
        for i, region_idx in enumerate(vor.point_region):
            if i >= num_points:  # Skip the corner points
                continue
                
            region = vor.regions[region_idx]
            
            if -1 not in region and len(region) > 0:  # Skip unbounded regions
                # Get polygon vertices
                polygon = [vor.vertices[v] for v in region]
                if len(polygon) >= 3:  # Need at least 3 points for a polygon
                    # Select color based on position or index
                    color_idx = int((points[i][0] / width + points[i][1] / height) * 127) % len(palette.colors)
                    color = palette.colors[color_idx]
                    
                    # Plot polygon
                    poly = plt.Polygon(
                        polygon,
                        fill=True,
                        color=color,
                        alpha=0.8,
                        edgecolor='black',
                        linewidth=edge_width,
                    )
                    ax.add_patch(poly)
                    
        # Set axis limits
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        
        # Remove axes for artistic effect
        ax.set_axis_off()
        plt.tight_layout(pad=0)
        
        # Store the figure
        self._figure = fig
        
        # Convert figure to image
        self._figure_to_image()
        
    def _generate_l_system(self) -> None:
        """
        Generate art using an L-system (Lindenmayer system).
        """
        import math
        
        # Get parameters with defaults
        width, height = self.resolution
        axiom = self.params.get("axiom", "F")
        rules = self.params.get("rules", {"F": "F+F-F-F+F"})
        iterations = self.params.get("iterations", 3)
        angle = self.params.get("angle", 90)
        line_width = self.params.get("line_width", 1.5)
        
        # Apply L-system rules
        current = axiom
        for _ in range(iterations):
            next_gen = ""
            for char in current:
                if char in rules:
                    next_gen += rules[char]
                else:
                    next_gen += char
            current = next_gen
            
        # Get color palette
        palette_name = self.params.get("color_palette", "autumn")
        palette = ColorPalette.get_palette(palette_name)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100, facecolor='black')
        
        # Set up initial position and direction
        pos = np.array([0.1 * width, 0.1 * height])
        direction = 0  # Angle in degrees
        
        # Set up stack for storing positions and directions
        stack = []
        
        # Set up list to store all lines for efficient plotting
        lines = []
        
        # Track drawing bounds to ensure it fits on canvas
        min_x, max_x = pos[0], pos[0]
        min_y, max_y = pos[1], pos[1]
        
        # Parse and draw the L-system
        for i, char in enumerate(current):
            if char == 'F':  # Move forward and draw a line
                # Calculate new position
                rad = math.radians(direction)
                new_pos = pos + np.array([math.cos(rad), math.sin(rad)]) * (width / (iterations * 10))
                
                # Store line segment
                lines.append([pos[0], pos[1], new_pos[0], new_pos[1]])
                
                # Update position
                pos = new_pos
                
                # Update bounds
                min_x = min(min_x, pos[0])
                max_x = max(max_x, pos[0])
                min_y = min(min_y, pos[1])
                max_y = max(max_y, pos[1])
                
            elif char == '+':  # Turn left
                direction += angle
            elif char == '-':  # Turn right
                direction -= angle
            elif char == '[':  # Push current state onto stack
                stack.append((pos.copy(), direction))
            elif char == ']':  # Pop state from stack
                pos, direction = stack.pop()
                
        # Calculate scaling to fit the drawing on the canvas
        x_range = max_x - min_x
        y_range = max_y - min_y
        if x_range > 0 and y_range > 0:
            scale = min(0.8 * width / x_range, 0.8 * height / y_range)
            offset_x = width / 2 - (min_x + x_range / 2) * scale
            offset_y = height / 2 - (min_y + y_range / 2) * scale
            
            # Scale and translate all lines
            scaled_lines = []
            for line in lines:
                x1, y1, x2, y2 = line
                scaled_lines.append([
                    x1 * scale + offset_x,
                    y1 * scale + offset_y,
                    x2 * scale + offset_x,
                    y2 * scale + offset_y,
                ])
                
            # Draw all lines with color gradient
            num_lines = len(scaled_lines)
            for i, line in enumerate(scaled_lines):
                # Calculate color index based on line position
                progress = i / num_lines
                color_idx = int(progress * (len(palette.colors) - 1))
                color = palette.colors[color_idx]
                
                # Draw the line segment
                ax.plot(
                    [line[0], line[2]],
                    [line[1], line[3]],
                    color=color,
                    linewidth=line_width,
                    alpha=0.8,
                )
        
        # Set axis limits
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        
        # Remove axes for artistic effect
        ax.set_axis_off()
        plt.tight_layout(pad=0)
        
        # Store the figure
        self._figure = fig
        
        # Convert figure to image
        self._figure_to_image()
        
    def _generate_cellular_automata(self) -> None:
        """
        Generate art using cellular automata (e.g., Conway's Game of Life).
        """
        # Get parameters with defaults
        width, height = self.resolution
        rule = self.params.get("rule", 30)  # Rule 30 is chaotic and interesting
        generations = self.params.get("generations", height)
        initial_state = self.params.get("initial_state", None)
        
        # Set up the cellular automaton grid
        cells = np.zeros((generations, width), dtype=np.uint8)
        
        # Initialize the first row
        if initial_state is None:
            # Default: single cell in the middle
            cells[0, width // 2] = 1
        else:
            # Use provided initial state or random
            if initial_state == "random":
                cells[0] = np.random.randint(0, 2, width)
            else:
                for i, val in enumerate(initial_state[:width]):
                    cells[0, i] = 1 if val else 0
                    
        # Generate subsequent generations using the specified rule
        for i in range(1, generations):
            for j in range(width):
                # Get the three cells above (with wraparound)
                left = cells[i-1, (j-1) % width]
                center = cells[i-1, j]
                right = cells[i-1, (j+1) % width]
                
                # Convert the three cells to a binary pattern (0-7)
                pattern = (left << 2) | (center << 1) | right
                
                # Apply the rule
                cells[i, j] = 1 if (rule & (1 << pattern)) != 0 else 0
                
        # Get color palette
        palette_name = self.params.get("color_palette", "grayscale")
        palette = ColorPalette.get_palette(palette_name)
        
        # Create a figure
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        
        # Plot the cellular automaton
        ax.imshow(
            cells,
            cmap=palette.cmap,
            interpolation='nearest',
            aspect='auto',
            extent=[0, width, 0, height],
        )
        
        # Remove axes for artistic effect
        ax.set_axis_off()
        plt.tight_layout(pad=0)
        
        # Store the figure
        self._figure = fig
        
        # Convert figure to image
        self._figure_to_image()
        
    def _generate_reaction_diffusion(self) -> None:
        """
        Generate art using a reaction-diffusion system (e.g., Gray-Scott model).
        """
        # Get parameters with defaults
        width, height = self.resolution
        iterations = self.params.get("iterations", 50)
        du = self.params.get("diffusion_rate_a", 0.16)
        dv = self.params.get("diffusion_rate_b", 0.08)
        f = self.params.get("feed_rate", 0.035)
        k = self.params.get("kill_rate", 0.065)
        dt = self.params.get("time_step", 1.0)
        seed_type = self.params.get("seed_type", "center")
        
        # Gray-Scott reaction-diffusion implementation
        # Initialize with values for A (activator) and B (inhibitor)
        u = np.ones((height, width), dtype=np.float64)  # Substance U
        v = np.zeros((height, width), dtype=np.float64)  # Substance V
        
        # Create seed
        if seed_type == "random":
            for i in range(10):
                y = np.random.randint(height)
                x = np.random.randint(width)
                r = np.random.randint(3, 10)
                y_idxs, x_idxs = np.ogrid[-r:r+1, -r:r+1]
                mask = x_idxs**2 + y_idxs**2 <= r**2
                for yy in range(-r, r+1):
                    for xx in range(-r, r+1):
                        if mask[yy+r, xx+r]:
                            y_idx = (y + yy) % height
                            x_idx = (x + xx) % width
                            u[y_idx, x_idx] = 0.5
                            v[y_idx, x_idx] = 0.25
        else:  # Default: center
            r = min(width, height) // 4
            center_y, center_x = height // 2, width // 2
            y_idxs, x_idxs = np.ogrid[-r:r+1, -r:r+1]
            mask = x_idxs**2 + y_idxs**2 <= r**2
            for y in range(-r, r+1):
                for x in range(-r, r+1):
                    if mask[y+r, x+r]:
                        y_idx = (center_y + y) % height
                        x_idx = (center_x + x) % width
                        u[y_idx, x_idx] = 0.5
                        v[y_idx, x_idx] = 0.25
                        
        # Run the simulation
        for _ in range(iterations):
            # Calculate Laplacian
            laplace_u = (
                np.roll(u, 1, axis=0) + np.roll(u, -1, axis=0) +
                np.roll(u, 1, axis=1) + np.roll(u, -1, axis=1) - 4 * u
            )
            
            laplace_v = (
                np.roll(v, 1, axis=0) + np.roll(v, -1, axis=0) +
                np.roll(v, 1, axis=1) + np.roll(v, -1, axis=1) - 4 * v
            )
            
            # Gray-Scott equations
            uvv = u * v * v
            u_next = u + dt * (du * laplace_u - uvv + f * (1 - u))
            v_next = v + dt * (dv * laplace_v + uvv - (f + k) * v)
            
            u, v = u_next, v_next
            
        # Get color palette
        palette_name = self.params.get("color_palette", "ocean")
        palette = ColorPalette.get_palette(palette_name)
        
        # Create a figure
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        
        # Plot the result (v is usually more visually interesting)
        ax.imshow(
            v,
            cmap=palette.cmap,
            interpolation='bicubic',
            aspect='auto',
            extent=[0, width, 0, height],
        )
        
        # Remove axes for artistic effect
        ax.set_axis_off()
        plt.tight_layout(pad=0)
        
        # Store the figure
        self._figure = fig
        
        # Convert figure to image
        self._figure_to_image()
        
    def _generate_fractal_tree(self) -> None:
        """
        Generate art using a recursive fractal tree algorithm.
        """
        import math
        
        # Get parameters with defaults
        width, height = self.resolution
        depth = self.params.get("depth", 9)
        init_angle = self.params.get("initial_angle", 90)  # Degrees
        branch_angle = self.params.get("branch_angle", 25)  # Degrees
        shrink_factor = self.params.get("shrink_factor", 0.7)
        init_length = self.params.get("initial_length", height / 3)
        variation = self.params.get("variation", 0.2)  # Random variation factor
        line_width = self.params.get("line_width", 1.5)
        
        # Get color palette
        palette_name = self.params.get("color_palette", "forest")
        palette = ColorPalette.get_palette(palette_name)
        
        # Create a figure
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
        
        # Function to draw a branch recursively
        def draw_branch(x, y, length, angle, branch_depth, ax):
            if branch_depth <= 0:
                return
                
            # Calculate end point
            angle_rad = math.radians(angle)
            end_x = x + length * math.cos(angle_rad)
            end_y = y + length * math.sin(angle_rad)
            
            # Determine color based on branch depth
            color_idx = int((depth - branch_depth) / depth * (len(palette.colors) - 1))
            color = palette.colors[color_idx]
            
            # Draw the branch
            ax.plot(
                [x, end_x],
                [y, end_y],
                color=color,
                linewidth=line_width * (branch_depth / depth),
                alpha=0.8,
            )
            
            # Add variation to parameters
            left_var = 1.0 + variation * (np.random.random() - 0.5)
            right_var = 1.0 + variation * (np.random.random() - 0.5)
            left_angle_var = branch_angle * (1.0 + variation * (np.random.random() - 0.5))
            right_angle_var = branch_angle * (1.0 + variation * (np.random.random() - 0.5))
            
            # Recursively draw left and right branches
            draw_branch(
                end_x, end_y,
                length * shrink_factor * left_var,
                angle + left_angle_var,
                branch_depth - 1,
                ax
            )
            
            draw_branch(
                end_x, end_y,
                length * shrink_factor * right_var,
                angle - right_angle_var,
                branch_depth - 1,
                ax
            )
            
        # Draw the initial trunk
        start_x = width / 2
        start_y = height * 0.1
        draw_branch(start_x, start_y, init_length, init_angle, depth, ax)
        
        # Set axis limits
        ax.set_xlim(0, width)
        ax.set_ylim(0, height)
        
        # Remove axes for artistic effect
        ax.set_axis_off()
        plt.tight_layout(pad=0)
        
        # Store the figure
        self._figure = fig
        
        # Convert figure to image
        self._figure_to_image()
        
    def _figure_to_image(self) -> None:
        """Convert the matplotlib figure to a numpy image array."""
        import io
        
        if self._figure is None:
            return
            
        # Save figure to a buffer
        buf = io.BytesIO()
        self._figure.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # Load buffer with PIL and convert to numpy array
        img = Image.open(buf)
        self.image = np.array(img)
        
    def save(self, output_path: str) -> str:
        """
        Save the generated art to a file.
        
        Args:
            output_path: Path where the file should be saved
            
        Returns:
            The path to the saved file
            
        Raises:
            ValueError: If no image has been generated
        """
        if self.image is None:
            raise ValueError("No image generated. Generate art first.")
            
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # Convert numpy array to PIL Image and save
        img = Image.fromarray(self.image)
        img.save(output_path)
        
        return output_path
        
    def show(self) -> None:
        """
        Display the generated art.
        
        Raises:
            ValueError: If no image has been generated
        """
        if self._figure is None:
            raise ValueError("No image generated. Generate art first.")
            
        plt.figure(self._figure.number)
        plt.show()
        
    def __repr__(self) -> str:
        """Return a string representation of the ProceduralArt object."""
        if self.image is None:
            return f"ProceduralArt(algorithm='{self.algorithm}', not generated)"
            
        return f"ProceduralArt(algorithm='{self.algorithm}', {self.image.shape[1]}x{self.image.shape[0]})" 