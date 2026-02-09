# Agent
: information_theory

## Scope
 This directory contains information_theory components for the module. It provides 5 classes and 25 functions.

## Classes
 and Functions

### ChannelCapacityCalculator
 Channel capacity calculator for spatial communication.

**Methods**:
- `calculate(channel_matrix: Optional[np.ndarray], signal_power: Optional[float], noise_power: Optional[float], method: str) -> float`: Calculate channel capacity.
- `spatial_capacity(coordinates: np.ndarray, signal_power: np.ndarray, noise_power: float, **kwargs) -> float`: Calculate spatial channel capacity.
- `waterfilling(channel_gains: np.ndarray, noise_power: float, total_power: float) -> Tuple[np.ndarray, float]`: Calculate optimal power allocation using waterfilling.

### EntropyCalculator
 Entropy calculator for spatial data.

**Methods**:
- `calculate(data: np.ndarray, method: str, **kwargs) -> float`: Calculate entropy for given data.
- `spatial_entropy(coordinates: np.ndarray, values: Optional[np.ndarray], method: str, **kwargs) -> float`: Calculate spatial entropy.
- `conditional_entropy(probabilities_xy: np.ndarray, probabilities_y: np.ndarray) -> float`: Calculate conditional entropy.
- `joint_entropy(probabilities_xy: np.ndarray) -> float`: Calculate joint entropy.

### KLDivergenceCalculator
 KL divergence calculator for spatial data.

**Methods**:
- `calculate(p: np.ndarray, q: np.ndarray, method: str) -> float`: Calculate divergence between distributions.
- `spatial_kl_divergence(coordinates_p: np.ndarray, values_p: np.ndarray, coordinates_q: np.ndarray, values_q: np.ndarray, **kwargs) -> float`: Calculate spatial KL divergence.

### MutualInformationCalculator
 mutual information calculator for spatial data.

**Methods**:
- `calculate(probabilities_xy: np.ndarray, probabilities_x: np.ndarray, probabilities_y: np.ndarray, normalized: bool, normalization: str) -> float`: Calculate mutual information.
- `spatial_mutual_information(coordinates_x: np.ndarray, values_x: np.ndarray, coordinates_y: np.ndarray, values_y: np.ndarray, **kwargs) -> float`: Calculate spatial mutual information.
- `conditional_mutual_information(probabilities_xyz: np.ndarray, probabilities_xz: np.ndarray, probabilities_yz: np.ndarray, probabilities_z: np.ndarray) -> float`: Calculate conditional mutual information.

### SpatialCodingCalculator
 Spatial coding and compression calculator.

**Methods**:
- `compress(coordinates: np.ndarray, values: np.ndarray, method: str, **kwargs) -> Tuple[np.ndarray, Dict[str, Any]]`: Compress spatial data.
- `encode(data: np.ndarray, method: str, **kwargs) -> Tuple[bytes, Dict[str, Any]]`: Apply entropy coding.
- `efficiency(original_data: np.ndarray, encoded_data: Union[np.ndarray, bytes], **kwargs) -> float`: Calculate encoding efficiency.

### channel_capacity
 `channel_capacity(channel_matrix: np.ndarray, noise_power: Optional[float], power_constraint: Optional[float], base: float) -> float` Calculate channel capacity for a discrete memoryless channel.

### spatial_channel_capacity
 `spatial_channel_capacity(coordinates: np.ndarray, signal_power: np.ndarray, noise_power: float, path_loss_exponent: float, base: float) -> float` Calculate channel capacity for spatial communication system.

### awgn_channel_capacity
 `awgn_channel_capacity(signal_power: float, noise_power: float, bandwidth: float, base: float) -> float` Calculate capacity of Additive White Gaussian Noise (AWGN) channel.

### mimo_channel_capacity
 `mimo_channel_capacity(channel_matrix: np.ndarray, noise_power: float, power_constraint: Optional[float], base: float) -> float` Calculate capacity of Multiple-Input Multiple-Output (MIMO) channel.

### waterfilling_power_allocation
 `waterfilling_power_allocation(channel_gains: np.ndarray, noise_power: float, total_power: float, base: float) -> Tuple[np.ndarray, float]` Calculate optimal power allocation using waterfilling algorithm.

### shannon_entropy
 `shannon_entropy(probabilities: np.ndarray, base: float, normalize: bool) -> float` Calculate Shannon entropy for a probability distribution.

### renyi_entropy
 `renyi_entropy(probabilities: np.ndarray, alpha: float, base: float) -> float` Calculate Renyi entropy for a probability distribution.

### tsallis_entropy
 `tsallis_entropy(probabilities: np.ndarray, q: float, base: float) -> float` Calculate Tsallis entropy for a probability distribution.

### spatial_entropy
 `spatial_entropy(coordinates: np.ndarray, values: Optional[np.ndarray], method: str, bins: Optional[Union[int, Tuple[int, int]]], bandwidth: Optional[float]) -> float` Calculate spatial entropy for point patterns or spatial data.

### conditional_entropy
 `conditional_entropy(probabilities_xy: np.ndarray, probabilities_y: np.ndarray, base: float) -> float` Calculate conditional entropy H(X|Y).

### joint_entropy
 `joint_entropy(probabilities_xy: np.ndarray, base: float) -> float` Calculate joint entropy H(X,Y).

### kl_divergence
 `kl_divergence(p: np.ndarray, q: np.ndarray, base: float, epsilon: float) -> float` Calculate Kullback-Leibler divergence D_KL(P||Q).

### js_divergence
 `js_divergence(p: np.ndarray, q: np.ndarray, base: float, epsilon: float) -> float` Calculate Jensen-Shannon divergence D_JS(P||Q).

### spatial_kl_divergence
 `spatial_kl_divergence(coordinates_p: np.ndarray, values_p: np.ndarray, coordinates_q: np.ndarray, values_q: np.ndarray, bins: Optional[Union[int, Tuple[int, int]]], base: float, method: str) -> float` Calculate KL divergence between two spatial distributions.

### symmetric_kl_divergence
 `symmetric_kl_divergence(p: np.ndarray, q: np.ndarray, base: float, epsilon: float) -> float` Calculate symmetric KL divergence.

### renyi_divergence
 `renyi_divergence(p: np.ndarray, q: np.ndarray, alpha: float, base: float, epsilon: float) -> float` Calculate Renyi divergence D_α(P||Q).

### mutual_information
 `mutual_information(probabilities_xy: np.ndarray, probabilities_x: np.ndarray, probabilities_y: np.ndarray, base: float) -> float` Calculate mutual information I(X;Y).

### conditional_mutual_information
 `conditional_mutual_information(probabilities_xyz: np.ndarray, probabilities_xz: np.ndarray, probabilities_yz: np.ndarray, probabilities_z: np.ndarray, base: float) -> float` Calculate conditional mutual information I(X;Y|Z).

### spatial_mutual_information
 `spatial_mutual_information(coordinates_x: np.ndarray, values_x: np.ndarray, coordinates_y: np.ndarray, values_y: np.ndarray, bins: Optional[Union[int, Tuple[int, int]]], base: float, distance_threshold: Optional[float]) -> float` Calculate mutual information between two spatial datasets.

### normalized_mutual_information
 `normalized_mutual_information(probabilities_xy: np.ndarray, probabilities_x: np.ndarray, probabilities_y: np.ndarray, base: float, normalization: str) -> float` Calculate normalized mutual information.

### spatial_encoding_efficiency
 `spatial_encoding_efficiency(original_data: np.ndarray, encoded_data: Union[np.ndarray, bytes], method: str) -> float` Calculate encoding efficiency for spatial data.

### compression_ratio
 `compression_ratio(original_size: int, compressed_size: int) -> float` Calculate compression ratio.

### coding_gain
 `coding_gain(original_snr: float, encoded_snr: float, method: str) -> float` Calculate coding gain.

### spatial_compression
 `spatial_compression(coordinates: np.ndarray, values: np.ndarray, method: str, compression_level: float) -> Tuple[np.ndarray, Dict[str, Any]]` Compress spatial data using various methods.

### entropy_coding
 `entropy_coding(data: np.ndarray, method: str) -> Tuple[bytes, Dict[str, Any]]` Apply entropy coding to spatial data.

## Capabilities

- **5 classes** for core functionality
- **25 functions** for utility operations

## Integration

- **Location**: `src/geo_infer_math/core/information_theory`
- **Type**: Directory Node
