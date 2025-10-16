using MediatR;

namespace NuIeee.Application.Features.Events.Commands;

public record DeleteEventCommand(Guid Id) : IRequest<bool>;