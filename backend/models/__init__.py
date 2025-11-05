"""Models package for backend."""
from .shared import (
    AIFunctionResult,
    TriggerResponse,
    ErrorResponse,
    BatchProcessingStatus,
    IngestionResult,
    HealthCheck
)

from .controls import (
    ControlsListItem,
    ControlsRawData,
    ControlsAIResults,
    ControlsDetails,
    ControlsList
)

from .external_loss import (
    ExternalLossListItem,
    ExternalLossRawData,
    ExternalLossAIResults,
    ExternalLossDetails,
    ExternalLossList
)

from .internal_loss import (
    InternalLossListItem,
    InternalLossRawData,
    InternalLossAIResults,
    InternalLossDetails,
    InternalLossList
)

from .issues import (
    IssuesListItem,
    IssuesRawData,
    IssuesAIResults,
    IssuesDetails,
    IssuesList
)

__all__ = [
    # Shared models
    'AIFunctionResult',
    'TriggerResponse',
    'ErrorResponse',
    'BatchProcessingStatus',
    'IngestionResult',
    'HealthCheck',

    # Controls models
    'ControlsListItem',
    'ControlsRawData',
    'ControlsAIResults',
    'ControlsDetails',
    'ControlsList',

    # External loss models
    'ExternalLossListItem',
    'ExternalLossRawData',
    'ExternalLossAIResults',
    'ExternalLossDetails',
    'ExternalLossList',

    # Internal loss models
    'InternalLossListItem',
    'InternalLossRawData',
    'InternalLossAIResults',
    'InternalLossDetails',
    'InternalLossList',

    # Issues models
    'IssuesListItem',
    'IssuesRawData',
    'IssuesAIResults',
    'IssuesDetails',
    'IssuesList'
]
