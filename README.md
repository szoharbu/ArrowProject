
# Arrow

Arrow is an architecture-agnostic, direct-to-random stimuli generator designed for architectural and micro-architectural contexts. 
It generates diverse stimuli, workloads and scenarios to evaluate and stress-test a wide range of architectures, enabling comprehensive analysis and optimization of system performance. 
With its flexible design, Arrow is ideal for researchers and engineers assessing architectural decisions across various environments.

## Features

- Architecture-agnostic design: Not tied to any specific hardware or architecture.
- Dynamic, template-driven generation: Adapts to user inputs and intent with configurable knobs and user-tailored scenarios.
- Generate random assembly stimuli for architectural and micro-architectural analysis.
- Evaluate system performance under diverse workloads and edge cases.
- Extensible library for adding custom workflows, stimuli, and use cases.
- Supports input/output operations for automated validation pipelines.
- Easily integrates with front-end frameworks like Streamlit.
- Built with flexibility for confidential internal usage.
- Full direct to random spectrum: from targeted corner cases to fully random, large-scale scenarios for comprehensive feature coverage.


## Getting Started

This guide will walk you through setting up the project environment and dependencies. Follow these steps to ensure the project is ready to run.

### Prerequisites

Before you begin, make sure you have the following installed:

- **Python**: Version 3.12 or later
- **Git**: For cloning the repository
- **PyCharm (optional)**: For an enhanced development experience


### Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/szoharbu/ArrowProject.git
   cd project
   ```

2. **Run the Setup Script**

   To set up the project environment:

   - **For Non-PyCharm Users**:
  Follow the [Setup Instructions for Non-PyCharm Users](Docs/setup_basic.md).

   - **For PyCharm Users**:
  Follow the [Setup Instructions for PyCharm Users](Docs/setup_pycharm.md).



### Running the Tool

Run the main script to start using Arrow:
      `python Arrow/main.py <your template>`

For PyCharm Users, simply run the `direct_run` configuration from PyCharm

## License

Arrow is licensed under the GNU General Public License v3.0. See the [LICENSE](./LICENSE) file for details.

## Contributions

Contributions are welcome! If you'd like to contribute:
1. Fork the repository.
2. Create a new branch for your changes.
3. Submit a pull request for review.

By contributing, you agree that your contributions will be licensed under the GPL-3.0.

See [CONTRIBUTING.md](.Docs/CONTRIBUTING.md) for more details.

## Future Intentions

While Arrow is currently open-source under the GPL-3.0, I plan to explore monetization options in the future, including:
- Offering premium features or services.
- Providing enterprise licensing for specific use cases.
- Selling commercial licenses for organizations requiring proprietary extensions.

The current open-source version and its license will remain unaffected. Future versions or components may be released under different terms.

## FAQ

### Understanding the GPL License and Its Impact on Your Project
### 1. Can I use this tool in my project without sharing my code?
      Yes, absolutely! The GNU General Public License (GPL-3.0) does not impose any restrictions on private/internal use.
      You can freely use this tool, modify it, and even integrate it into your workflows without sharing your modifications, as long as you are not distributing the tool or its modified versions to others.
### 2. Are there any usage limitations?
      No, the GPL license imposes no restrictions on how you use the tool or the outputs it generates.
      You are free to use the tool for testing, development, or any other business need without any additional obligations.
### 3. What happens if I want to modify the tool?
      You can modify the tool for your internal purposes without any requirement to share your changes.
      The only scenario where you need to share your modifications is if you distribute the modified tool to others (e.g., clients, partners, or the public).
### 4. Why is this tool licensed under GPL instead of MIT?
      The GPL license ensures that the tool remains an open, collaborative project by:
      Preventing others from cloning, modifying, and releasing proprietary versions that could compete with the original.
      Encouraging shared contributions while protecting the openness of the tool.
      In contrast, permissive licenses like MIT allow anyone to repackage the tool as a closed-source product, potentially fragmenting the community and undermining collaborative growth.

### 5. Does the GPL license affect my internal extensions or workflows?
      No, the GPL license does not affect your internal extensions, workflows, or proprietary IP.
      You can create proprietary extensions or workflows using the tool, as long as you do not distribute the modified core tool externally.

### 6. What if we distribute the tool or a modified version to others?
      If you distribute the tool (or a modified version) externally, you must release the source code under GPL-3.0.

### 7. Can we extend the tool with proprietary content?
      Yes. You can create proprietary extensions or use the tool in confidential workflows, as long as you do not distribute the modified core tool to others.

## Contact

For questions, support, or inquiries about commercial use, please contact:

Zohar Buchris
Email: szoharbu@gmail.com

