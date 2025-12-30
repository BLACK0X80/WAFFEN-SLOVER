"""
Prompt templates for Waffen-Solver LLM interactions.

Contains all prompt templates used for error analysis,
solution generation, explanations, and translations.
"""


class PromptTemplates:
    """
    Central repository for all prompt templates.

    Provides structured templates for different LLM operations
    with variable substitution support.
    """

    SYSTEM_PROMPT: str = """You are Waffen-Solver, an expert AI debugging assistant. Your role is to analyze errors, identify root causes, and provide comprehensive solutions.

You have deep expertise in:
- All major programming languages and frameworks
- System architecture and design patterns
- Debugging methodologies and best practices
- Code quality and performance optimization

When analyzing errors:
1. Carefully parse the error message and stack trace
2. Identify the error type and category
3. Determine the root cause with high confidence
4. Consider the broader context and potential contributing factors

When providing solutions:
1. Offer multiple solution approaches when applicable
2. Explain trade-offs between different solutions
3. Rank solutions by effectiveness and implementation complexity
4. Provide clear, actionable implementation steps

Always be precise, thorough, and educational in your responses."""

    ERROR_ANALYSIS_TEMPLATE: str = """Analyze the following error and provide a structured analysis:

ERROR:
{error_message}

STACK TRACE:
{stack_trace}

CONTEXT:
{context}

Provide your analysis in the following JSON format:
{{
    "error_type": "the type/category of error",
    "severity": "critical|high|medium|low",
    "root_cause": "detailed explanation of the root cause",
    "contributing_factors": ["list", "of", "factors"],
    "affected_components": ["list", "of", "components"],
    "confidence": 0.0 to 1.0
}}"""

    SOLUTION_GENERATION_TEMPLATE: str = """Based on the following error analysis, generate solution options:

ERROR ANALYSIS:
{analysis}

CODEBASE CONTEXT:
{codebase_context}

GIT CONTEXT:
{git_context}

Generate solutions in the following JSON format:
{{
    "solutions": [
        {{
            "title": "solution title",
            "approach": "detailed approach description",
            "implementation": "code or step-by-step implementation",
            "pros": ["list", "of", "advantages"],
            "cons": ["list", "of", "disadvantages"],
            "complexity": "low|medium|high",
            "risk_level": "low|medium|high",
            "time_estimate": "estimated time",
            "best_for": ["list", "of", "use cases"]
        }}
    ]
}}"""

    SIMPLE_EXPLANATION_TEMPLATE: str = """Explain this error in simple terms that a beginner programmer would understand:

ERROR: {error_message}

ROOT CAUSE: {root_cause}

Provide a clear, jargon-free explanation using analogies if helpful. The explanation should be 2-3 paragraphs maximum."""

    TECHNICAL_EXPLANATION_TEMPLATE: str = """Provide a technical explanation of this error for an experienced developer:

ERROR: {error_message}

ROOT CAUSE: {root_cause}

CONTEXT: {context}

Include relevant technical details, language-specific behavior, and best practices for handling this type of error."""

    DEEP_DIVE_EXPLANATION_TEMPLATE: str = """Provide an in-depth technical deep dive on this error:

ERROR: {error_message}

ROOT CAUSE: {root_cause}

CONTEXT: {context}

STACK TRACE: {stack_trace}

Include:
1. Underlying mechanisms that caused this error
2. How the language/runtime handles this scenario
3. Historical context or common patterns that lead to this
4. Prevention strategies and architectural considerations
5. Related errors or edge cases to be aware of"""

    TRANSLATION_TEMPLATE: str = """Translate the following technical content to {target_language}.

CONTENT:
{content}

INSTRUCTIONS:
- Preserve all code snippets, file paths, and technical identifiers
- Translate explanations and descriptions
- Maintain the original formatting and structure
- Use appropriate technical terminology in the target language"""

    CODEBASE_LEARNING_TEMPLATE: str = """Analyze the following codebase structure and extract key patterns:

PROJECT STRUCTURE:
{structure}

FILE SAMPLES:
{samples}

Identify and describe:
1. Architectural style and patterns
2. Coding conventions used
3. Key abstractions and interfaces
4. Dependency relationships
5. Error handling patterns"""

    GIT_ANALYSIS_TEMPLATE: str = """Analyze the Git history context for debugging insights:

RECENT COMMITS:
{commits}

FILE HISTORY:
{file_history}

BLAME INFO:
{blame_info}

Provide insights about:
1. Recent changes that might be related to the error
2. Patterns in the change history
3. Potentially fragile areas of the codebase
4. Suggested commits to investigate"""

    @classmethod
    def get_template(cls, name: str) -> str:
        """
        Get a template by name.

        Args:
            name: Name of the template attribute.

        Returns:
            The template string.

        Raises:
            AttributeError: If template name does not exist.
        """
        return getattr(cls, name)

    @classmethod
    def format_template(cls, name: str, **kwargs: str) -> str:
        """
        Get and format a template with provided values.

        Args:
            name: Name of the template attribute.
            **kwargs: Values to substitute in the template.

        Returns:
            Formatted template string.
        """
        template = cls.get_template(name)
        return template.format(**kwargs)
