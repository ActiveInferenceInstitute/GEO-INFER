# The Location Protocol specification - A standardized framework for working with location information on the decentralized web
https://easierdata.org/updates/2025/2025-05-19-location-protocol-spec

In collaboration with Astral, we’ve been designing a standardized framework for working with location information on the decentralized web. The goal of this work is to enrich the emerging decentralized geospatial web with established geospatial standards, making it easier to create and share geographic data and services in a decentralized manner, but also bringing novel mechanisms for verifiability, transparency, and trust to the web more generally.

An initial version of the Location Protocol specification is detailed below, including

the motivation for the protocol,

an outline of the core metadata model,

how to use the protocol to record location-based records, and

some demonstrations and potential real-world use-cases.

What is the Location Protocol?
The Location Protocol provides a common format for portable, signed records of spatial information — including coordinates, boundaries, imagery, and other geospatial data. It works across decentralized and conventional systems, enabling consistency, attribution, and verifiability. The protocol is intended for anyone working with geographic data in contexts that require interoperability, transparency, or trust. A Location Protocol record is a digitally signed, self-contained unit of spatial data — structured like a row in a geospatial database, but portable and cryptographically verifiable. Some records make a claim that might need to be trusted or verified (for example, “I was here at this time”), while others simply describe a place, boundary, or asset. All records are signed to ensure integrity and authorship, and can be shared publicly, held privately, or disclosed selectively. When needed, a record can include location proofs — artifacts such as cryptographic evidence or sensor data that help others assess whether a claim is accurate. This structure allows both people and systems to evaluate what a record says, who authored it, whether it’s been changed — and whether it should be believed.

The Location Protocol allows independent applications to exchange and interpret spatial data — whether tied to the Earth’s surface, a virtual environment, or another digital location context. It’s designed to support an extensible range of geospatial feature types, data formats, and location proofs.

It is an open specification for structuring and signing spatial data so others can verify its origin, integrity, and meaning. And it’s implementation-agnostic: any system that follows the spec — whether on-chain, off-chain, or peer-to-peer — can produce records that are fully interoperable.

In our reference implementation, built on the Ethereum Attestation Service, these signed records are called location attestations. That term comes from EAS, but the concept is broader: any signed record that conforms to the protocol — regardless of how or where it’s created — qualifies. EAS provides a powerful and well-documented framework for defining schemas, managing attestations, and storing them either onchain or offchain. It made it easy for us to prototype and deploy quickly, but the protocol itself does not depend on EAS or any specific infrastructure. Others are free to implement it using different signature schemes, storage layers, or verification workflows, as long as they follow the same structural rules.

In practice, each location attestation wraps a structured Location Protocol (LP) payload inside an EAS attestation. The payload contains the spatial data and any additional fields defined by the protocol. EAS handles the signing and metadata — including author, timestamp, and schema — and optionally stores the record onchain. The result is a portable, verifiable unit of spatial information. While we use EAS here, any system that follows the same structure and signing rules can produce fully compatible location attestations.

Why now?
The Web3 paradigm, which includes consensus networks, blockchains, smart contracts, content-addressed data, decentralized identifiers, and more, introduces new architectural constraints and opportunities for geospatial data. Well-designed Web3 systems are more open and durable, and enhance user rights by incorporating features such as user-controlled accounts, immutability, attribution, tamper-evidence, and selective disclosure. However, current geospatial systems were never designed to interoperate with distributed ledgers or peer-to-peer networks. On top of this, decentralized systems typically do not offer structured and standardized methods for working with geospatial data, which requires special handling.

The Location Protocol is grounded in established geospatial standards while embracing the design principles of the decentralized web. It provides a minimal, extensible foundation for working with spatial data across systems — enabling records that are compatible with existing tools and also cryptographically signed for verification, attribution, and selective disclosure. By treating location as a first-class data type, the protocol helps bridge traditional geospatial practices with decentralized architectures, making it easier for diverse applications to interoperate, evaluate claims, and exchange trustworthy spatial information.

This structure supports a wide range of use cases — from building location-based applications on smart contracts, to verifying where compute operations took place (e.g. for compliance or emissions reporting), to enabling digital MRV and localized AI agent behavior. Wherever location matters and trust is required, the protocol offers a common language to structure and verify spatial information.

The Location Protocol specification
The Location Protocol specification is built around a location payload. This geospatial data artifact includes a digital signature verifying its source, structured metadata about location attributes, and potentially some additional supporting fields. At a minimum, a valid location payload must include a few base fields. Still, it can be extended with composable fields to provide more context, and can also leverage EAS properties for additional functionality. Below, an outline is provided for the base fields, which can support many different representations of location information, and a description of the composable fields and properties.

The Location Protocol specification guides the construction of a LP payload. This geospatial data artifact includes structured metadata about location attributes, potentially some additional supporting fields, and can be digitally signed to verify its source . At a minimum, a valid LP payload must include a few base fields — but it can be enriched with composable fields to provide more context. EAS also natively includes additional data — we describe EAS properties that can be leveraged for additional functionality. Below, an outline is provided for the base fields, which can support many different representations of location information, and a description of the composable fields and properties.

Base fields
The LP payload must contain the fields below at a minimum to identify and represent the location information.

Field Name

Type

Description

srs[1]

string

The spatial / symbolic reference system used to represent the location data.

locationType

string

The format / type of location data being represented.

location

string, int40[2], int40[2][], int40[2][][]

The actual location data

specVersion

uint8

The version of the specification used to generate the attestation.

Supported location types
The locationType field identifies the format and / or type of location data being represented in the location field. The locationType field is essential for interoperability across platforms and downstream applications, as it enables applications to interpret location data correctly. This flexibility allows developers to choose the most appropriate format (i.e. locationType ) for their specific use case while maintaining interoperability.

Any location type structure can be defined — this field is extensible by design. We are working on developing a Location Format Extensions Library that will eventually support the following location types:

Location Type

Additional Details

Data Type

Example

coordinate-decimal[2]

Decimal coordinates with values ordered as longitude then latitude

any

-122.4194, 37.7749,

dms

Latitude and longitude coordinates in degrees, minutes, and seconds

string

37°46'30.0"N 122°25'10.0"W

scaledCoordinates[2][3]

A scaled integer representation of coordinate pairs, representing points lines or polygons

int40[2], int40[2][], int40[2][][]

[[-74000000, 40700000], [-74100000, 40700000], [-74100000, 40800000], [-74000000, 40800000], [-74000000, 40700000]]

geoJson

A GeoJSON object representing a geographic feature as points, lines, or polygons

string

{ "type": "Point", "coordinates": [ -122.4194, 37.7749 ] }

wkt

A WKT (Well-Known Text) representation of a geometric object as points, lines, or polygons

string

POINT(-122.4194 37.7749)

placeNames

Known place names

string

San Francisco, CA, Eiffel Tower

address

Standard mailing address

string

1600 Amphitheatre Parkway, Mountain View, CA 94043

h3

A hierarchical hexagonal grid system used for spatial indexing

string, uint64

8928308280fffff

geohash

A hierarchical spatial data structure which subdivides space into buckets of grid shape

string, uint64

u4pruyd

w3w

A geocoding system that encodes geographic coordinates into three dictionary words

string

apple.banana.orange

mgrs

A military grid reference system used for geospatial referencing

string

33TWN0000000000

utm

A universal transverse mercator coordinate system used for mapping

string

33TWN0000000000

spcs

Comma-separated x, y coordinates in a state plane coordinate system

string

2000000, 500000 in a specific state plane zone

The location value is interpreted based on the locationType field, and location cannot be decoded without first resolving locationType.

Composable fields
A LP payload may also include additional fields that describe, support, or verify different aspects of the encoded location information. These composable fields can be grouped by (a) “common fields” and (b) “proof fields”.

Common fields
The location payload supports additional fields that may be common to many location attestations, but nevertheless are optional. These fields provide further information about the context of an attestation, such as a textual description (i.e., “memo”), when the location information was recorded (i.e., eventTimeStamp), or other values associated with the location (i.e., attributes). The composable nature of location attestation objects allows for the inclusion of additional arbitrary fields that may be relevant to specific use cases or applications. For instance, the mediaData field could store a pointer to photographic or video evidence, perhaps on IPFS or the Filecoin network, that supports or enhances the context of the location attestation. This could be useful to record the exact location of damage caused by artillery in civilian zones, the location of unexploded munitions, or the location of emergency response requests during a natural disaster. In each case, using the Location Protocol ensures the location information is structured and recorded in a way that ensures it is accessible and interoperable, while also remaining extensible with media and other fields to contextualize the location record. This allows maximal flexibility in how a location attestation is composed, disseminated, and consumed. An example of this being particularly useful might be one or more decentralized applications allowing individuals to record calls for aid during an emergency. Organizations or agencies, with other missions and resources, might consume this information across different time horizons and respond differently based on the context provided by a photo linked by the mediaData field.

These “common fields” below cover those currently recognized by our downstream API but could be expanded based on community feedback and emergent usage patterns.

The LP payload supports additional fields that may be common to many types of applications and location attestations, but nevertheless are optional. These fields provide further information about the context of an attestation, such as a textual description (i.e., memo), when the location information was recorded (i.e., eventTimeStamp).

The composable nature of LP payloads allows for the inclusion of additional arbitrary fields that may be relevant to specific use cases or applications. For instance, the mediaData field could store a pointer to photographic or video evidence, perhaps on IPFS, that supports or enhances the context of a location attestation. This could be useful to record the precise location of damage caused by artillery in civilian zones, the location of unexploded munitions, or the location of emergency response requests during a natural disaster. The mediaType field specifies the type of media as defined by a MIME-type-style string, such as image/jpeg, video/mp4, application/pdf or other supporting formats. In each case, using the Location Protocol ensures the location information is structured and recorded in a way that ensures it is accessible and interoperable, while also potentially being enriched with media and other fields to contextualize the location record. This allows maximal flexibility in how a location attestation is composed, disseminated, and consumed. An example of this being particularly useful might be one or more decentralized applications allowing individuals to record different types of calls for aid during an emergency. Organizations or agencies, with varying missions and resources, might consume this information across different time horizons and respond differently based on the context provided by a photo linked by the mediaData field.

These “common fields” below cover those currently recognized by our downstream API but could be expanded based on community feedback and emergent usage patterns.

Field Name

Type

Description

mediaData[4]

bytes, bytes32, string

A bytes array representing the actual media data. Could also be a bytes32 array or string representation of a CID referencing the media data stored on IPFS.

mediaType

string

A MIME-type-style string describing the media data, such as image/jpeg, video/mp4, or application/pdf.

eventTimeStamp

uint64

The UNIX timestamp of the event associated with the location record. Note, this should not be confused with the time field that represents when the attestation was created.

recipient

address

The address of the recipient of the attestation.

memo

string

An arbitrary message or note.

…

any[5]

An arbitrary field to extend the base model.

Proof fields
The LP payload can include fields incorporating corroborating evidence to prove the authenticity and accuracy of the location information, sometimes without revealing an exact location. A location proof is a mechanism for verifying the location of something with a degree of certainty, which would otherwise require some form of technical and/or social manipulation in order to forge. The proof fields are optional but recommended for use cases that require a higher level of confidence. The recipeType field serves a similar purpose to the locationType field and dictates how the evidence stored in the proof field should be handled. These proof fields can significantly enhance the credibility and utility of a location attestation, elevating it to a LP compliant location proof. Though still under development, it is envisioned that the Location Protocol will support a handful of proof strategies with varying levels of technical complexity, guarantee of precision, and degree of privacy preservation, which could also be combined to further support an attestation.

Field Name

Type

Description

recipePayload

byte32

The proof of the authenticity and integrity of the location data.

recipeType

string

The type of proof used to verify the location data.

EAS properties
The Location Protocol provides a flexible framework that enables interoperability across various applications and blockchains. As mentioned previously, the reference implementation of the Location Protocol is utilizes the Ethereum Attestation Service (EAS) and the EAS SDK to create, sign, verify, and distribute Location Protocol-compliant location attestations.

All EAS attestations, whether stored on the blockchain (on-chain) or off the blockchain (off-chain), share certain common properties that can be associated with the LP payload. There are minor differences between the properties used for creating an attestation and those available when retrieving an attestation, though the two sets are generally similar. The following tables highlight these properties, which allow the location attestations to interact with the broader EAS system.

Properties for creating attestations

Property Name

Type

Description

Required

schemaString

string

The schema string that defines the structure of the data to be attested.

:heavy_check_mark:

schemaUID

byte32

The unique schema identifier associated with the attestation.

:heavy_check_mark:

refUID

byte32

The reference UID of the attestation, if any.

expirationTime

uint64

The Unix timestamp when the attestation expires (0 for no expiration).

recipient

address

The address of the recipient of the attestation.

time

uint64

The UNIX timestamp of when the attestation was created. (offchain only)

:heavy_check_mark:

revocable

bool

A boolean indicating whether the attestation is revocable.

data

bytes

The location payload.

:heavy_check_mark:

value

uint256

The ETH value that is being sent with the attestation. (onchain only)

The schemaString and schema UID properties define the structure of the data being attested to on EAS, while the refUIDproperty links attestations together. The expirationTime property sets a time limit on the validity of the attestation on EAS, while the recipient property specifies who will receive it. Once an attestation is created, it is signed and then possibly stored on the blockchain, returning a UID representing the created attestation.

Properties when retrieving attestations

On EAS, an attestation is retrievable by its UID, a 32-byte hash, to identify the attestation on the blockchain. In addition, the following properties are returned when an attestation is retrieved from the blockchain:

Property Name

Type

Description

uid

byte32

The unique identifier of the attestation.

schemaString

string

The schema string that defines the structure of the data to be attested.

schemaUID

byte32

The unique schema identifier associated with the attestation.

refUID

byte32

The reference UID of the attestation, if any.

time

uint64

The UNIX timestamp of when the attestation was created.

expirationTime

uint64

The Unix timestamp when the attestation expires (0 for no expiration).

revocationTime

uint64

The Unix timestamp when the attestation was revoked, if applicable.

recipient

address

The address of the recipient of the attestation.

attester

address

The address of the attester who created the attestation.

revocable

bool

A boolean indicating whether the attestation is revocable.

data

bytes

The location payload.


Ultimately, the LP payload is part of the more general EAS attestation object, extending the data model to support the Location Protocol while remaining extremely flexible.

Using the Location Protocol and EAS to create location attestations
Below is an example of how the Location Protocol is used with the Ethereum Attestation Service (EAS) to make digitally signed location attestations. Introducing Location Protocol compliance ensures that these location attestations remain interoperable geospatial digital artifacts.

Step 1: Define a schema
The first step is to define the schema string that specifies the structure of a LP payload, which is eventually attached to an attestation object (i.e., via the data field). Note that we will maintain a set of core schemas to simplify use — but you can also create your own schema for any reason.

A schema outlines the data format and represents a string containing data types and fields. The following is an example of how a schema string is defined:

`<dataType> <fieldName>, <dataType> <fieldName>, ...`
where <dataType> is the type of data (e.g., string, uint8, int40[2], etc.) and <fieldName> is the name of the field.

Schema strings must conform to the Location Protocol base model, meaning it must contain at least the following four fields and have appropriate data types — but it can be expanded as needed.

const schemaString =
  "string srs, string locationType, string location, uint8 specVersion";
A schema on EAS must first be registered. This allows users to leverage pre-existing schemas or create new ones as needed, though it is envisioned that a collection of commonly used schemas will be made available for users to easily use. Here is an example of how to register a schema:

import { SchemaRegistry } from "@ethereum-attestation-service/eas-sdk";
import { ethers } from "ethers";

const schemaRegistryContractAddress =
  "0x0a7E2Ff54e76B8E6659aedc9103FB21c038050D0"; // Sepolia Schema Registry v0.26 on testnet
const schemaRegistry = new SchemaRegistry(schemaRegistryContractAddress);

schemaRegistry.connect(signer);

const schemaString =
  "string srs, string locationType, string location, uint8 specVersion";
const revocable = true;

const transaction = await schemaRegistry.register({
  schemaString,
  revocable,
});

const schemaUid = await transaction.wait();

console.log("Registered Schema UID:", schemaUid);
Once registered, the schema can be viewed on the EAS schema registry here. The registration process will generate a schema UID, a unique 32-byte hash of the schema string, which is needed to make attestations. Generating a schema UID independently of registration is also possible, though we won’t cover that here.

The following schema UID was generated based on the schema string above:

"0xedd6b005e276227690314960c55a3dc6e088611a709b4fbb4d40c32980640b9a"
Step 2: Prepare a location payload
At its core, an EAS attestation is a formalized assertion or claim about something, in this case, a location. This could be a physical address, a GPS coordinate, or other form of location data. As mentioned above, the schema string defines the location information format (i.e., locationPayload below) that will be encoded and subsequently passed into the attestation object. In the example below, latitude and longitude coordinates are assigned to location, the type of coordinates (decimal degrees) is assigned to locationType, and the specific ESPG code denoting the spatial reference system is assigned to srs. The value for specVersion represents the version of the Location Protocol specification.

At its core, an EAS attestation is a formalized assertion or claim about something. In our case, it’s a claim about a location. This could be a physical address, a GPS coordinate, or other form of location data. As mentioned above, the schema string defines the location information format (i.e., locationPayload below) that will be encoded and subsequently passed into the attestation object. In the example below, latitude and longitude coordinates are assigned to location, the type of coordinates (decimal degrees) is assigned to locationType, and the specific ESPG code denoting the spatial reference system is assigned to srs. The value for specVersion represents the version of the Location Protocol specification.

const locationPayload = [
  { name: "location", value: "44.967243, -103.771556", type: "string" },
  { name: "locationType", value: "coordinate-decimal+lon-lat", type: "string" },
  { name: "srs", value: "EPSG:4326", type: "string" },
  { name: "specVersion", value: 1, type: "uint8" },
];
Step 3: Encode the location payload
Before creating an attestation object, a schemaEncoder object is instantiated using the schema string to encode a LP payload (i.e., locationPayload). The encoding process ensures that the data conforms to the structure defined by the schema associated with the attestation. Why is this encoding necessary?

On-chain Validation: Smart contracts rely on structured data to verify the integrity and correctness of an attestation. The SchemaEncoder ensures the data adheres to the schema’s format, making it possible for on-chain logic (e.g., verification or revocation) to process the data reliably.

Consistency and Interoperability: By encoding data according to a defined schema, different systems and parties can interpret and validate the data uniformly, ensuring compatibility across applications and platforms. This interoperability extends beyond on-chain attestations to off-chain scenarios where someone may create an attestation without broadcasting it globally. Instead, they might selectively share access with specific services or applications, which could then further distribute the information while maintaining the same standardized format. Whether stored on-chain, off-chain, or shared peer-to-peer, the consistent schema structure ensures that location attestations remain interpretable and verifiable across all systems that implement the Location Protocol specification.

Creating the schemaEncoder object based on schemaString and encoding locationPayload can be done as follows:

const schemaEncoder = new SchemaEncoder(schemaString);
const encodedData = schemaEncoder.encodeData(locationPayload);
which returns the following result:

0x000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000009455053473a343332360000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e646563696d616c44656772656573000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001634342e3936373234332c202d3130332e37373135353600000000000000000000
It is possible to verify this encoding with any ETH ABI Decoder tool such as this. Just paste the encoding into the input box and enter the schema field types in the order they appear in the schema string. For example, for the above encoding, string, string, string, uint8 would be entered as the types.

The encoded locationPayload is then passed into the data property of the attestation object.

Step 4: Create the attestation object
The attestation object contains EAS properties, one of which is the data property that contains the encoded LP payload. The following illustrates the structure of an attestation object:

const attestationOjbect = {
  schema: schemaUID,
  data: {
    recipient: "0xFD50b031E778fAb33DfD2Fc3Ca66a1EeF0652165", // Example Ethereum address of the recipient of the attestation
    expirationTime: 0,
    data: encodedData,
  },
};
After the attestation is signed, submitted, and added to the blockchain, a UID is generated that can be used to query the attestation and view its details. Here is a resultant attestation UID for an attestation that incorporates the LP payload from above.

Attestation UID: 0x628f06c011351ef39b419718f29f20f0bc62ff3342d1e9c284531bf12bd20f31

EAS Explorer Link: https://sepolia.easscan.org/attestation/view/0x628f06c011351ef39b419718f29f20f0bc62ff3342d1e9c284531bf12bd20f31

Example of creating an On-Chain Location Attestation with the EAS SDK
The following TypeScript code snippet demonstrates all four steps to create a location attestation compliant with the Location Protocol, using the EAS SDK as the reference implementation.

1    import { EAS, SchemaEncoder } from "@ethereum-attestation-service/eas-sdk";
2
3    const eas = new EAS(EASContractAddress);
4    eas.connect(signer);
5
6    // defining the schema string
7    const schemaString = "string srs, string locationType, string location, uint8 specVersion"
8
9    // Create the location payload
10   const locationPayload = [
11     { name: "srs", value: "EPSG:4326", type: "string" },
12     { name: "locationType", value: "coordinate-decimal+lon-lat", type: "string" },
13     { name: "location", value: "-103.771556, 44.967243", type: "string" },
14     { name: "specVersion", value: 1, type: "uint8" }
15   ]
16
17   // Initialize SchemaEncoder with the schema string
18   const schemaEncoder = new SchemaEncoder(schemaString);
19   const encodedData = schemaEncoder.encodeData(locationPayload)
20
21   const schemaUID = "0xedd6b005e276227690314960c55a3dc6e088611a709b4fbb4d40c32980640b9a";
22
23   const attestationOjbect = {
24     schema: schemaUID,
25     data: {
26       recipient: "0xFD50b031E778fAb33DfD2Fc3Ca66a1EeF0652165", // Example Ethereum address of the recipient of the attestation
27       expirationTime: 0,
28       data: encodedData,
29      },
30   }
31
32   const tx = await eas.attest(attestationOjbect);
33
34   const newAttestationUID = await tx.wait();
35
36   console.log("New attestation UID:", newAttestationUID);
To recap, line 1 imports the EAS SDK and the SchemaEncoder class. Line 3 creates an instance of the EAS class, which is used to interact with the Ethereum Attestation Service. Line 4 connects the EAS instance to a signer used to sign transactions. Lines 7 - 15 define the schema string that structures the LP payload. Lines 18-19 generate the schema encoder object to encode the LP payload. In lines 23-30, an attestation object contains the encoded LP payload and the schema UID of the registered schema string. The attestation object is submitted on line 32, and line 34 returns the UID of the attestation submission once the transaction is complete.

Patterns and strategies demonstrating the use of the Location Protocol
The following examples demonstrate how geographical information can be recorded, integrated, and attested to using the Location Protocol and leveraging the Ethereum Attestation Service (EAS). To simplify the process, we have developed a set of helper functions that streamline tasks such as registering a schema, encoding the location payload, and preparing an attestation for submission. These capabilities will ultimately be bundled into an SDK, along with extensive type-checking, making it easier for developers to build decentralized geospatial applications (more coming soon in a subsequent blog post). Therefore, the primary focus here is to demonstrate variations in how the LP payload is created in each example based on the Location Protocol specification.

1. Event Check-in using GeoIP
This example demonstrates how location attestations could be used to verify attendance at an event. The Typescript app uses the device’s IP address to record location and create an attestation. This could be used for events like concerts, conferences, or any other event where verifying attendance for an event could be helpful. Here, we have extended the base model by incorporating two optional composable fields and one custom extensible field. The eventTimestamp is the time of the event, while the ticketId is a unique identifier for the ticket purchased.

// 1. Get the provider and signer
const { signer } = getProviderSigner();

// Register schema if not already registered. Will return the schema UID if already registered
const schemaString = "string srs, string locationType, string location, uint8 specVersion, uint64 eventTimestamp, string ticketId"
const schemaUID = await registerSchema(signer, schemaString);

// Grab the IP Address of the mobile device and use GeoIP to get the location
// then apply to the appropriate fields in the locationPayload
const ipAddress = await publicIpv4();
const locationData = geoip.lookup(ipAddress);
const geoJsonPoint = {
    type: "Point",
    coordinates: [locationData.ll[1], locationData.ll[0]]
};
const geoJsonPointString = JSON.stringify(geoJsonPoint);
const locationPayload = [
    { name: "srs", value: "EPSG:4326", type: "string" },
    { name: "locationType", value: "geojson-point", type: "string" },
    { name: "location", value: geoJsonPointString, type: "string" },
    { name: "specVersion", value: 1, type: "uint8" },
    { name: "eventTimestamp", Math.floor(time.getTime() / 1000), type: "uint64" },
    { name: "ticketId", value: "ticket-1234567890", type: "string" }
  ]

// Create the attestation object
const attestationObject = {
  recipient: "0xFD50b031E778fAb33DfD2Fc3Ca66a1EeF0652165",
  revocable: true,
  schemaUID: schemaUID,
  schemaString: schemaString,
  dataToEncode: locationPayload
};

const newAttestationUID = await createOnChainAttestation(signer, attestationData);
2. Using a QR code for geocaching
This example demonstrates how a QR code could be used for geocaching, treasure hunts, or location-based gaming events. The application would first scan a QR code embedded with geospatial metadata, then format the geospatial metadata according to the Location Protocol, and finally trigger the generation of an attestation on EAS. In this case, the QR code metadata is mapped to the base model field location as scaled coordinates, and two optional composable fields are also used. The first is the memo field, representing a note or message associated with the geocache, while the second is the eventTimestamp field, representing the time the QR code was scanned.

This example illustrates how a QR code can be utilized for geocaching, treasure hunts, or location-based gaming events where a user’s actions can be verified. The application would first

scan a QR code embedded with geospatial metadata and some secret,

format the geospatial metadata according to the Location Protocol,

generate a location proof by hashing the encoded secret with their wallet address

and finally trigger the generation of an attestation on EAS.

In this case, the QR code metadata is mapped to the base model field location as scaled coordinates, and two optional composable fields are also used. The first is the memo field, which represents a note or message associated with the geocache, while the second is the eventTimestamp field, representing the time the QR code was scanned. Since the location attestation is signed and stamped on-chain, a user’s actions are transparent and can be verified against their wallet id. Because they include the hashed secret + address, the event organizer can verify that they had the correct secret — evidence that they were present at the geocache location. (Granted, it’s weak evidence — it’d be trivial to text a picture of the QR code to someone who wasn’t actually there — but since this would require a form collusion, the hash is considered a location proof.)

// The signer object created in this example is tied to the user's wallet id
const { signer } = getProviderSigner(); //

// Register schema if not already registered. Will return the schema UID if already registered
const schemaString: "string srs, string locationType, uint40[2][] location, uint40 specVersion, uint64 eventTimestamp, string memo";
const schemaUID = await registerSchema(signer, schemaString);

// Extract QR code metadata and apply to the appropriate fields in the `locationPayload` variable
const qrData = await decodeQR(imagePath) // Returns {lat: <latitude coordinate>, long: <longitude coordinate>, secret: <secret>}
const proof = hash(qrData.secret, signer.address)

const locationPayload = [
    { name: "srs", value: "EPSG:4326", type: "string" },
    { name: "locationType", value: "scaledCoordinates", type: "string" },
    { name: "location", value: [qrData.lat, qrData.long], type: "uint40[2][]" },
    { name: “recipeType”, value: [“geocache-secret-v1.0”], type: “string[]” },
    { name: "recipePayload", value: [proof], type: "bytes[]" },
    { name: "specVersion", value: 1, type: "uint8" },
    { name: "eventTimestamp", value: Math.floor(time.getTime() / 1000), type: "uint64" },
    { name: "memo", value: qrData.note, type: "string" }
  ]

// Create the attestation object
const attestationObject = {
  recipient: "0xFD50b031E778fAb33DfD2Fc3Ca66a1EeF0652165",
  revocable: true,
  schemaUID: schemaUID,
  schemaString: schemaString
  dataToEncode: locationPayload
};

const newAttestationUID = await createOnChainAttestation(signer, attestationData);
3. Preserving and sharing verified photograph metadata generated by Proofmode
This example demonstrates how the Location Protocol can support the preservation and dissemination of metadata generated by ProofMode, a mobile app for capturing verifiable photos. A verified photo from ProofMode includes information about the media and location information that can be easily parsed into a Location Protocol-compliant attestation for further verification and downstream use. The Location Protocol can be adapted here through the use of the proof fields of a LP payload. In this case, the recipeType is set to “ProofMode”, and the recipePayload field contains the hash of the image file since the photos EXIF data contains the location. A third-party system or user can audit the location attestation using the metadata supplied in the proof fields as evidence and verify using one of ProofMode’s tools.

We can also include composable fields to capture metadata about some of the media generated by Proofmode. For example, the mediaData field is assigned to a bytes array representing the photo, or more likely a CID pointing to the photo and reducing the overall storage footprint, mediaType is a MIME-type-style string describing the media datatype, and the memo field contains any additional notes. Meanwhile, the location field is set to the decimal degree coordinates of the photo, and the eventTimestamp represents the time the image was taken. This strategy could be particularly valuable for applications requiring verified media evidence, such as journalism, human rights documentation, legal evidence collection, and scientific field research, where the authenticity and provenance of the location of media are critical.

// 1. Get the provider and signer
const { signer } = getProviderSigner();

// Register schema if not already registered. Will return the schema UID if already registered
const schemaString: "string srs, string locationType, string location, uint40 specVersion, uint40 eventTimestamp, string memo, string mediaType, bytes media";
const schemaUID = await registerSchema(signer, schemaString);

// Extract the ProofMode zip file and grab the metadata, then apply it to the appropriate fields in the locationPayload
const files = extractZipFile(zipFilePath, extractDir);
const proofModeData = getProofModeMetadata(files);
const locationPayload = [
    { name: "srs", value: "EPSG:4326", type: "string" },
    { name: "locationType", value: "coordinate-decimal+lon-lat", type: "string" },
    { name: "location", value: proofModeData.location, type: "string" },
    { name: "specVersion", value: 1, type: "uint8" },
    { name: "eventTimestamp", BigInt(proofModeData.timestamp), type: "uint64" },
    { name: "memo", value: proofModeData.notes, type: "string" },
    { name: "mediaType", value: proofModeData.mediaType, type: "string" },
    { name: "mediaData", value: proofModeData.media, type: "bytes" },
    { name: "recipeType", value: "ProofMode", type: "string" }
    { name: "recipePayload", value: proofModeData.fileHash, type: "string" },
  ]

// Create the attestation object
const attestationObject = {
  recipient: "0xFD50b031E778fAb33DfD2Fc3Ca66a1EeF0652165",
  revocable: true,
  schemaUID: schemaUID,
  schemaString: schemaString,
  dataToEncode: locationPayload
};

const newAttestationUID = await createOnChainAttestation(signer, attestationData);

These three demonstrative strategies are just a few of the many possible recipes that app developers can use to create Location Protocol-compliant attestations, ensuring that location information is verifiable, transparent, interoperable, and trustworthy on the decentralized web. Importantly, app developers can expand or combine these strategies to create new recipes that bring additional verifiability and security to location information. Ongoing work includes the development of a library of recipes for using the Location Protocol to make more complex and extensible location attestations, including those that include formal location proofs as evidence. It also includes the development of an SDK for creating location attestations compliant with the Location Protocol, which, along with the recipe library, will streamline application development.

Some potential applications of the Location Protocol
Touch-Grass
The Touch Grass app provides a fun and interactive way to encourage people to spend time outdoors. As users “touch grass”, it allows them to record these moments to prove they were outside — an informal type of location attestation. First, the app checks if they are in an outdoor area, such as a park or nature reserve. Once confirmed, it then records the details of the user being outside and uses their wallet address to sign a secure digital ledger so it can’t be changed or erased. Users can see their history of outdoor events, view a global map of where others have touched grass, and even compete on a leaderboard to see who is the most active outdoors. The Location Protocol could be used to formalize the location attestations made by the Touch Grass app, unlocking many potential ways for users to record themselves touching grass and allowing this information to be accessed more widely.

Kolektivo
Kolektivo empowers local communities in Curaçao to restore ecosystems and improve food security through regenerative agriculture. The project leverages decentralized technology, community currencies, and decentralized governance to ensure transparent, equitable resource allocation and to incentivize sustainable practices. Using the Location Protocol, regenerative agricultural stewards could share wind data collected from different types of local weather instruments and use that data to create attestations. This would help verify the weather stations’ location and the data collected from them, providing interoperable records to be used collectively for understanding extreme weather events.

M3tering
The M3tering Protocol is a blockchain-based initiative designed to combat energy poverty in underserved sub-Saharan Africa and Latin America regions through decentralized solar energy production incentivized through tokenized rewards. Participants can become electricity providers by installing rooftop solar systems and earn protocol tokens based on their energy output, fostering a self-reinforcing “DePIN flywheel effect” that drives infrastructure growth. By leveraging smart contracts to ensure the immutable tracking of energy data and automated payments, along with a decentralized governance model (DAO) that empowers communities to manage resources transparently, M3tering aims to democratize access to clean energy while reducing reliance on centralized systems. Integrating the Location Protocol could enable smart contracts to execute geospatial logic that automatically adjusts based on various conditions, introducing location-aware incentives. Incentives could include solar irradiance levels at specific coordinates (e.g., rooftop arrays in sunnier regions earn more tokens), proximity to high-demand areas, or accounting for geographic risk factors such as flood-prone zones receiving bonus tokens for resilient installations.

Whiteflag Protocol
The Whiteflag Protocol utilizes blockchain technology to establish secure, decentralized communication channels in conflict zones, enabling stakeholders to share cryptographically verified messages, such as protected area designations or danger zone alerts, through immutable on-chain transactions authenticated via private keys and web resource control. Its standardized message schema supports seven functional categories, from emergency signals to resource coordination. At the same time, elliptic-curve encryption ensures sensitive data remains accessible only to intended recipients despite public blockchain visibility. Using the Location Protocol alongside Whiteflag could enable new functionality. For example, providing humanitarian organizations and other key stakeholders with a spatial lens for crisis mapping by delivering real-time, cryptographically signed geospatial data to improve the accuracy of conflict zone boundary markers and resource tracking.

Contribute to the Location Protocol and help build the decentralized geospatial web
The Location Protocol specification is a significant step towards creating a standardized framework for storing location data on the decentralized web. By leveraging the Ethereum Attestation Service (EAS), this initial reference implementation allows location attestations compliant with the Location Protocol to be created, signed, and verified for use across different platforms and applications, opening up new possibilities for producing, sharing, and valuing location information on the web.

As a result, we are excited to engage with the community and facilitate the use of the framework for building innovative applications and services that leverage location data. We encourage developers, researchers, and organizations to explore the Location Protocol specification and contribute to its development and use. We welcome feedback on any aspect of the specification, but in particular would be grateful to hear about the following:

What other fields or extensions should be considered?

Is there a location component (locationType) not included in the spec you use and would like to see included?

What applications or use cases would you like to see supported by the location protocol?

Flexibility is at the core of the Location Protocol, allowing the base model to be easily adapted for various use cases. Therefore, we are excited to learn how this framework can support your needs.

In summary, the Location Protocol treats location as a first-class primitive and represents a core element of the decentralized geospatial web. We look forward to fostering a community of stakeholders who are interested in building upon it and shaping its evolution. There is still much to do, including incorporating decentralized storage to support media and attribute tables, an SDK for streamlining the development of innovative applications and services that leverage location data, a comprehensive API for querying location attestations along with an interactive mapping interface, a Solidity library for verifiable geocomputation, and more. Together, we can build a more open, transparent, and trustworthy ecosystem for location data on the web!

[1]
It is recommended that the srs field conforms to EPSG code (e.g. EPSG:4326), OGC URN (e.g. urn:ogc:def:crs:OGC:1.3:CRS84), or a well-known identifier for the spatial reference system.

[2](1,2)
The preferred codified ordering for coordinate-decimal is longitude then latitude but it can be strictly set with a custom context option that’s appended to the end of coordinate-decimal. To codify the ordering as longitude then latitude the locationType is set as coordinate-decimal+lon-lat while codifying the ordering as latitude then longitude is set as coordinate-decimal+lat-lon.

[3]
It’s up to the implementor to set the precision and provide guidance on the default precision to be used. The maximum coordinate precision that can be set is 10⁹ as int40 can store values up to ±549,755,813. For example, a coordinate of 123.456 with a precision of 10¹⁰ would exceed the maximum value of int40 and would not be valid.

[4]
This data is intended to be irrelevant to the location proof and not required/utilized in the proof recipe verification.

[5]
The any type is a placeholder for any arbitrary field, following an acceptable Solidity ABI. Learn more about Solidity ABI types and the Contract ABI Specification here.