from enum import Enum


class Settings(Enum):
    # File Naming #
    OUTPUT_DIR: str
    BASE_NAME: str
    # Writen inside file #
    # Link 0 commands
    CORES: int
    MEMORY: int
    CHECKPOINT: bool
    # OLD_CHECKPOINT_START: str
    # Route section
    THEORY: str
    BASIS: str
    CALC_TYPE: str | list[str]
    # title section
    TITLE: str
    # Molecule specification
    CHARGE: int
    SPIN: int
    ATOMIC_COORDINATES: str  # could be supplied by file with @filename
    # ModRedundant
    MOD_RED: str  # could be supplied by file with @filename
