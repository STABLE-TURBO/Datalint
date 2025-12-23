#!/usr/bin/env python3
"""
Diagram Generation Script for DataLint

Generates comprehensive UML diagrams from the datalint codebase and updates README.md
"""

import subprocess
import ast
import re
from pathlib import Path
from typing import List, Dict, Set, Any


class CodeAnalyzer:
    """Analyzes Python codebase for diagram generation"""

    def __init__(self, source_dir: str = "datalint"):
        self.source_dir = Path(source_dir)
        self.classes: Dict[str, Dict[str, Any]] = {}
        self.modules: Dict[str, Set[str]] = {}
        self.functions: Dict[str, List[str]] = {}
        self.imports: Dict[str, Set[str]] = {}

    def analyze(self):
        """Analyze all Python files in the source directory"""
        for py_file in self.source_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            self._analyze_file(py_file)

    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            module_name = str(file_path.relative_to(self.source_dir)).replace('.py', '').replace('/', '.')

            self.modules[module_name] = set()
            self.functions[module_name] = []
            self.imports[module_name] = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._analyze_class(node, module_name)
                elif isinstance(node, ast.FunctionDef):
                    self.functions[module_name].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports[module_name].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports[module_name].add(node.module)

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

    def _analyze_class(self, node: ast.ClassDef, module_name: str):
        """Analyze a class definition"""
        class_info = {
            'name': node.name,
            'module': module_name,
            'methods': [],
            'attributes': [],
            'bases': [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
        }

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info['methods'].append({
                    'name': item.name,
                    'args': [arg.arg for arg in item.args.args]
                })
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info['attributes'].append(target.id)

        self.classes[f"{module_name}.{node.name}"] = class_info
        self.modules[module_name].add(node.name)


class DiagramGenerator:
    """Generates various UML diagrams"""

    def __init__(self, analyzer: CodeAnalyzer):
        self.analyzer = analyzer
        self.diagrams_dir = Path("docs/diagrams")

    def generate_all_diagrams(self):
        """Generate all diagram types"""
        self.diagrams_dir.mkdir(parents=True, exist_ok=True)

        # Structural Diagrams
        self.generate_class_diagram()
        self.generate_component_diagram()
        self.generate_deployment_diagram()
        self.generate_interface_diagram()

        # Behavioral Diagrams
        self.generate_sequence_diagram()
        self.generate_activity_diagram()
        self.generate_use_case_diagram()

    def generate_class_diagram(self):
        """Generate class diagram showing class hierarchy and relationships"""
        mermaid_content = "classDiagram\n"
        mermaid_content += "    class BaseValidator {\n"
        mermaid_content += "        <<abstract>>\n"
        mermaid_content += "        +String name*\n"
        mermaid_content += "        +ValidationResult validate(DataFrame df)*\n"
        mermaid_content += "        +String __repr__()\n"
        mermaid_content += "    }\n\n"

        mermaid_content += "    class Formatter {\n"
        mermaid_content += "        <<abstract>>\n"
        mermaid_content += "        +String format(List~ValidationResult~ results)*\n"
        mermaid_content += "    }\n\n"

        mermaid_content += "    class ValidationResult {\n"
        mermaid_content += "        +String name\n"
        mermaid_content += "        +String status\n"
        mermaid_content += "        +String message\n"
        mermaid_content += "        +List issues\n"
        mermaid_content += "        +List recommendations\n"
        mermaid_content += "        +Dict details\n"
        mermaid_content += "        +Boolean passed\n"
        mermaid_content += "        +Dict to_dict()\n"
        mermaid_content += "    }\n\n"

        mermaid_content += "    class ValidationRunner {\n"
        mermaid_content += "        -List~BaseValidator~ validators\n"
        mermaid_content += "        +ValidationRunner(List~BaseValidator~ validators)\n"
        mermaid_content += "        +void add_validator(BaseValidator validator)\n"
        mermaid_content += "        +List~ValidationResult~ run(DataFrame df)\n"
        mermaid_content += "        +Dict~String,ValidationResult~ run_dict(DataFrame df)\n"
        mermaid_content += "    }\n\n"

        # Concrete implementations (simplified)
        mermaid_content += "    class ConcreteValidator {\n"
        mermaid_content += "        +String name\n"
        mermaid_content += "        +ValidationResult validate(DataFrame df)\n"
        mermaid_content += "    }\n\n"

        mermaid_content += "    class ConcreteFormatter {\n"
        mermaid_content += "        +String format(List~ValidationResult~ results)\n"
        mermaid_content += "    }\n\n"

        # Relationships
        mermaid_content += "    BaseValidator <|.. ConcreteValidator : implements\n"
        mermaid_content += "    Formatter <|.. ConcreteFormatter : implements\n"
        mermaid_content += "    ValidationRunner --> BaseValidator : uses\n"
        mermaid_content += "    BaseValidator --> ValidationResult : returns\n"
        mermaid_content += "    ConcreteValidator --> ValidationResult : returns\n"

        self._generate_mermaid("class_diagram", mermaid_content)

    def generate_component_diagram(self):
        """Generate component diagram showing module relationships"""
        mermaid_content = "graph TD\n"
        mermaid_content += "    CLI[Command Line Interface]\n"
        mermaid_content += "    ENG[Core Validation Engine] \n"
        mermaid_content += "    UTI[Utility Functions]\n\n"
        mermaid_content += "    CLI --> ENG\n"
        mermaid_content += "    CLI --> UTI\n"
        mermaid_content += "    ENG --> UTI\n"

        self._generate_mermaid("component_diagram", mermaid_content)

    def generate_deployment_diagram(self):
        """Generate deployment diagram"""
        mermaid_content = "graph TD\n"
        mermaid_content += "    subgraph Local[Local Machine]\n"
        mermaid_content += "        Python[Python Environment]\n"
        mermaid_content += "        DataLint[DataLint Package]\n"
        mermaid_content += "    end\n"
        mermaid_content += "    Data[Data Files]\n"
        mermaid_content += "    Reports[Output Reports]\n\n"
        mermaid_content += "    DataLint --> Data\n"
        mermaid_content += "    DataLint --> Reports\n"
        mermaid_content += "    Python --> DataLint\n"

        self._generate_mermaid("deployment_diagram", mermaid_content)

    def generate_interface_diagram(self):
        """Generate interface diagram showing key interfaces and abstractions"""
        mermaid_content = "classDiagram\n"
        mermaid_content += "    class BaseValidator {\n"
        mermaid_content += "        <<abstract>>\n"
        mermaid_content += "        +name: str*\n"
        mermaid_content += "        +validate(df: DataFrame): ValidationResult*\n"
        mermaid_content += "    }\n\n"

        mermaid_content += "    class Formatter {\n"
        mermaid_content += "        <<abstract>>\n"
        mermaid_content += "        +format(results: List[ValidationResult]): str*\n"
        mermaid_content += "    }\n\n"

        mermaid_content += "    class ValidationResult {\n"
        mermaid_content += "        +name: str\n"
        mermaid_content += "        +status: Literal['passed', 'warning', 'failed']\n"
        mermaid_content += "        +message: str\n"
        mermaid_content += "        +issues: List\n"
        mermaid_content += "        +recommendations: List\n"
        mermaid_content += "        +details: Dict\n"
        mermaid_content += "        +passed: bool\n"
        mermaid_content += "        +to_dict(): Dict\n"
        mermaid_content += "    }\n\n"

        mermaid_content += "    class ValidationRunner {\n"
        mermaid_content += "        -validators: List[BaseValidator]\n"
        mermaid_content += "        +__init__(validators=None)\n"
        mermaid_content += "        +add_validator(validator: BaseValidator)\n"
        mermaid_content += "        +run(df: DataFrame): List[ValidationResult]\n"
        mermaid_content += "        +run_dict(df: DataFrame): Dict[str, ValidationResult]\n"
        mermaid_content += "    }\n\n"

        mermaid_content += "    BaseValidator <|.. ConcreteValidator : implements\n"
        mermaid_content += "    Formatter <|.. ConcreteFormatter : implements\n"
        mermaid_content += "    ValidationRunner --> BaseValidator : uses\n"
        mermaid_content += "    BaseValidator --> ValidationResult : returns\n"

        self._generate_mermaid("interface_diagram", mermaid_content)

    def generate_sequence_diagram(self):
        """Generate sequence diagram for validation workflow"""
        mermaid_content = "sequenceDiagram\n"
        mermaid_content += "    participant U as User\n"
        mermaid_content += "    participant C as CLI\n"
        mermaid_content += "    participant V as ValidationRunner\n"
        mermaid_content += "    participant B as BaseValidator\n"
        mermaid_content += "    participant D as DataFrame\n\n"

        mermaid_content += "    U->>C: datalint validate file.csv\n"
        mermaid_content += "    C->>V: run(df)\n"
        mermaid_content += "    loop for each validator\n"
        mermaid_content += "        V->>B: validate(df)\n"
        mermaid_content += "        B->>D: analyze data\n"
        mermaid_content += "        D-->>B: return analysis\n"
        mermaid_content += "        B-->>V: ValidationResult\n"
        mermaid_content += "    end\n"
        mermaid_content += "    V-->>C: results list\n"
        mermaid_content += "    C-->>U: formatted output\n"

        self._generate_mermaid("sequence_diagram", mermaid_content)

    def generate_activity_diagram(self):
        """Generate activity diagram for validation pipeline"""
        mermaid_content = "flowchart TD\n"
        mermaid_content += "    Start([Start])\n"
        mermaid_content += "    Run[User runs datalint validate]\n"
        mermaid_content += "    Parse[Parse command line arguments]\n"
        mermaid_content += "    Load[Load data file]\n"
        mermaid_content += "    Check{File loaded successfully?}\n"
        mermaid_content += "    Init[Initialize ValidationRunner]\n"
        mermaid_content += "    Validate[Run all validators]\n"
        mermaid_content += "    CheckResult{Validation passed?}\n"
        mermaid_content += "    Success[Generate success report]\n"
        mermaid_content += "    Fail[Generate failure report]\n"
        mermaid_content += "    Recomm[Show recommendations]\n"
        mermaid_content += "    Error[Show error message]\n"
        mermaid_content += "    Exit([Exit])\n\n"

        mermaid_content += "    Start --> Run\n"
        mermaid_content += "    Run --> Parse\n"
        mermaid_content += "    Parse --> Load\n"
        mermaid_content += "    Load --> Check\n"
        mermaid_content += "    Check -->|Yes| Init\n"
        mermaid_content += "    Init --> Validate\n"
        mermaid_content += "    Validate --> CheckResult\n"
        mermaid_content += "    CheckResult -->|Yes| Success\n"
        mermaid_content += "    CheckResult -->|No| Fail\n"
        mermaid_content += "    Fail --> Recomm\n"
        mermaid_content += "    Success --> Exit\n"
        mermaid_content += "    Recomm --> Exit\n"
        mermaid_content += "    Check -->|No| Error\n"
        mermaid_content += "    Error --> Exit\n"

        self._generate_mermaid("activity_diagram", mermaid_content)

    def generate_use_case_diagram(self):
        """Generate use case diagram"""
        mermaid_content = "flowchart LR\n"
        mermaid_content += "    DS([Data Scientist])\n"
        mermaid_content += "    MLE([ML Engineer])\n"
        mermaid_content += "    DevOps([DevOps Engineer])\n\n"

        mermaid_content += "    UC1[Validate Dataset]\n"
        mermaid_content += "    UC2[Learn from Clean Data]\n"
        mermaid_content += "    UC3[Profile Data Quality]\n"
        mermaid_content += "    UC4[Generate Reports]\n"
        mermaid_content += "    UC5[CI/CD Integration]\n\n"

        mermaid_content += "    DS --> UC1\n"
        mermaid_content += "    DS --> UC2\n"
        mermaid_content += "    MLE --> UC3\n"
        mermaid_content += "    DevOps --> UC5\n"
        mermaid_content += "    UC1 --> UC4\n"
        mermaid_content += "    UC2 --> UC4\n"
        mermaid_content += "    UC3 --> UC4\n"

        self._generate_mermaid("use_case_diagram", mermaid_content)

    def _generate_mermaid(self, name: str, content: str):
        """Generate Mermaid diagram file"""
        mermaid_file = self.diagrams_dir / f"{name}.mmd"

        # Write Mermaid file
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Generated Mermaid file: {mermaid_file}")

    def _generate_plantuml(self, name: str, content: str):
        """Generate PlantUML file"""
        plantuml_file = self.diagrams_dir / f"{name}.puml"

        # Write PlantUML file
        with open(plantuml_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Generated PlantUML file: {plantuml_file}")


class ReadmeUpdater:
    """Updates README.md with generated diagrams"""

    def __init__(self, diagrams_dir: Path = Path("docs/diagrams")):
        self.diagrams_dir = diagrams_dir
        self.readme_path = Path("README.md")

    def update_readme(self):
        """Update the README with diagram references"""
        if not self.readme_path.exists():
            return

        with open(self.readme_path, 'r') as f:
            content = f.read()

        # Find the architecture section
        arch_pattern = r'(### Architecture Diagrams\n\n).*?(\n---)'
        arch_match = re.search(arch_pattern, content, re.DOTALL)

        if arch_match:
            # Generate new diagrams section
            diagrams_section = self._generate_diagrams_section()

            # Replace the old section
            new_content = content.replace(arch_match.group(0), f"### Architecture Diagrams\n\n{diagrams_section}\n---")

            with open(self.readme_path, 'w') as f:
                f.write(new_content)

    def _generate_diagrams_section(self):
        """Generate the diagrams section for README"""
        diagrams = [
            ("Class Diagram", "class_diagram.mmd", "Shows the class hierarchy and relationships"),
            ("Interface Diagram", "interface_diagram.mmd", "Shows key interfaces and abstraction contracts"),
            ("Component Diagram", "component_diagram.mmd", "Illustrates high-level software components"),
            ("Deployment Diagram", "deployment_diagram.mmd", "Shows how the system is deployed"),
            ("Sequence Diagram", "sequence_diagram.mmd", "Displays the validation workflow sequence"),
            ("Activity Diagram", "activity_diagram.mmd", "Shows the validation pipeline activities"),
            ("Use Case Diagram", "use_case_diagram.mmd", "Illustrates user interactions with the system")
        ]

        section = ""
        for title, filename, description in diagrams:
            diagram_path = self.diagrams_dir / filename
            print(f"Checking diagram: {diagram_path} (exists: {diagram_path.exists()})")
            if diagram_path.exists():
                section += f"#### {title}\n"
                section += f"*{description}*\n\n"
                if filename.endswith('.mmd'):
                    # GitHub renders Mermaid natively
                    section += f"```mermaid\n"
                    with open(diagram_path, 'r', encoding='utf-8') as f:
                        section += f.read()
                    section += "\n```\n\n"
                elif filename.endswith('.puml'):
                    # GitHub can render PlantUML files directly
                    section += f"```plantuml\n"
                    with open(diagram_path, 'r', encoding='utf-8') as f:
                        section += f.read()
                    section += "\n```\n\n"
                else:
                    section += f"![{title}](docs/diagrams/{filename})\n\n"

        print(f"Generated section length: {len(section)}")
        return section


def main():
    """Main entry point"""
    print("🔍 Analyzing datalint codebase...")

    analyzer = CodeAnalyzer()
    analyzer.analyze()

    print("📊 Generating diagrams...")

    generator = DiagramGenerator(analyzer)
    generator.generate_all_diagrams()

    print("📝 Updating README...")

    updater = ReadmeUpdater()
    updater.update_readme()

    print("✅ Diagram generation complete!")


if __name__ == "__main__":
    main()
