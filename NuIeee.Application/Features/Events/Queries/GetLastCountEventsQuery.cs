using MediatR;
using NuIeee.Application.DTOs.Events;

namespace NuIeee.Application.Features.Events.Queries;

public record GetLastCountEventsQuery(int Count) : IRequest<List<EventDto>>;