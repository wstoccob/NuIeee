using MediatR;
using NuIeee.Application.Features.Events.Commands;
using NuIeee.Application.Interfaces;

namespace NuIeee.Application.Features.Events.Handlers;

public class DeleteEventCommandHandler(IEventRepository eventRepository) : IRequestHandler<DeleteEventCommand, bool>
{
    public async Task<bool> Handle(DeleteEventCommand request, CancellationToken cancellationToken)
    {
        var result = await eventRepository.DeleteEventAsync(request.Id, cancellationToken);
        
        return result;
    }
}