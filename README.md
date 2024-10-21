# PCR Open Source Thermocycler

This project was created as a seminar paper with the participation of students from Teplice High School. The goal of this project is to develop an open-source PCR thermocycler that can be used for a wide range of applications.

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [3D Model](#3d-model)
4. [Software](#software)
5. [Configuration File](#configuration-file)
6. [Installation](#installation)
7. [Usage](#usage)
8. [Contributing](#contributing)
9. [License](#license)

## Introduction
This project is open to the community and aims to provide an affordable and flexible PCR thermocycler. The system is designed to be customizable for various experimental needs.

## Features
- Open hardware design with a 3D printable model
- Software for controlling thermal cycles
- Easily configurable through an external configuration file
- Support for additional sensors and extensions

## 3D Model
The 3D model of the thermocycler is available in the `3d-model/` directory. This model is designed for standard FDM 3D printers. For detailed information on how to print and assemble the device, refer to the [Assembly Guide](3d-model/AssemblyGuide.md).

## Software
The software is designed to control the thermal cycle and manage the hardware. The source code is available in the `src/` directory. The software is written in Python and supports the following features:
- Setting temperature profiles
- Monitoring current temperature
- Automatic temperature regulation

### Basic Commands:

      # Install dependencies
      pip install -r requirements.txt
      
      # Run the application
      python main.py

## Configuration File

The configuration file config.json allows customization of temperature profiles and other device parameters. For more information on how to configure the system, see the Configuration Guide.

## Installation

For detailed information on how to install both hardware and software, please refer to the Installation Guide.

## Usage

This thermocycler can be used for various experimental purposes. More detailed usage instructions can be found in the Usage Guide.

## Contributing

This project welcomes contributions from the community. If you would like to contribute to the development, please refer to CONTRIBUTING.md for guidelines on how to get started.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
