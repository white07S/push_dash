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
    ControlsSearchRequest,
    ControlsList
)

from .external_loss import (
    ExternalLossListItem,
    ExternalLossRawData,
    ExternalLossAIResults,
    ExternalLossDetails,
    ExternalLossSearchRequest,
    ExternalLossList
)

from .internal_loss import (
    InternalLossListItem,
    InternalLossRawData,
    InternalLossAIResults,
    InternalLossDetails,
    InternalLossSearchRequest,
    InternalLossList
)

from .issues import (
    IssuesListItem,
    IssuesRawData,
    IssuesAIResults,
    IssuesDetails,
    IssuesSearchRequest,
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
    'ControlsSearchRequest',
    'ControlsList',

    # External loss models
    'ExternalLossListItem',
    'ExternalLossRawData',
    'ExternalLossAIResults',
    'ExternalLossDetails',
    'ExternalLossSearchRequest',
    'ExternalLossList',

    # Internal loss models
    'InternalLossListItem',
    'InternalLossRawData',
    'InternalLossAIResults',
    'InternalLossDetails',
    'InternalLossSearchRequest',
    'InternalLossList',

    # Issues models
    'IssuesListItem',
    'IssuesRawData',
    'IssuesAIResults',
    'IssuesDetails',
    'IssuesSearchRequest',
    'IssuesList'
]
