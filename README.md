# MPSecondJobs.org

[![Website](https://img.shields.io/website?url=https%3A%2F%2Fmpsecondjobs.org)](https://mpsecondjobs.org)  
[![GitHub](https://img.shields.io/github/license/messiosa/mpsecondjobs)](https://github.com/messiosa/mpsecondjobs/blob/main/LICENSE)

A platform for tracking and exploring second jobs held by Members of Parliament (MPs), with a focus on transparency and public accountability.

## Overview

**MPSecondJobs.org** is an open-source initiative to provide an accessible and searchable database of MPs' second jobs. This project is designed to encourage transparency and empower citizens to explore how representatives' outside income may intersect with their legislative responsibilities.

## Features

- **User-Friendly Interface**: An intuitive and easy-to-navigate platform.
- **Search and Filter**: Find specific MPs, job categories, or income levels.
- **Data Visualization**: Charts and graphs for quick insights into trends.
- **Open Data**: Freely available data for analysis and reuse.
- **Regular Updates**: Continuously updated with the latest disclosures.

## Live Site

Visit the live application at [MPSecondJobs.org](https://mpsecondjobs.org).

## Getting Started

### Prerequisites

- [Python](https://www.python.org/) (v3.7 or higher)
- [pip](https://pip.pypa.io/en/stable/)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/messiosa/mpsecondjobs.git
   cd mpsecondjobs
   ```

2. Set up a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python app.py
   ```

   The app will be available at `http://localhost:5000`.

### Deployment

Follow your hosting provider's documentation to deploy a Flask application. Make sure to set up environment variables and production settings as needed.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix:

   ```bash
   git checkout -b feature/my-feature
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add my feature"
   ```

4. Push to your fork:

   ```bash
   git push origin feature/my-feature
   ```

5. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/messiosa/mpsecondjobs/blob/main/LICENSE) file for details.

## Contact

For questions or feedback, please open an issue on [GitHub](https://github.com/messiosa/mpsecondjobs/issues).

---