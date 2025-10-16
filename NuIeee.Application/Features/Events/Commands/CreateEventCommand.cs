using MediatR;
using NuIeee.Application.DTOs.Events;

namespace NuIeee.Application.Features.Events.Commands;

public record CreateEventCommand(
    string Title,
    string Description,
    DateTime EventDateTime,
    Uri? RegistrationLink,
    List<EventPhotoDto> Photos
    ) : IRequest<Guid>;
