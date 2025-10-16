using MediatR;
using NuIeee.Application.DTOs.Events;

namespace NuIeee.Application.Features.Events.Queries;

public record GetEventByIdQuery(Guid id) : IRequest<EventDto>;