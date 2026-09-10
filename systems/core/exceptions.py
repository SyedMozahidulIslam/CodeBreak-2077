class CodeBreakError(Exception):
    pass


class CaseLoadError(CodeBreakError):
    pass


class CaseValidationError(CodeBreakError):
    pass


class SaveCorruptionError(CodeBreakError):
    pass


class AssetLoadError(CodeBreakError):
    pass


class ConfigError(CodeBreakError):
    pass
