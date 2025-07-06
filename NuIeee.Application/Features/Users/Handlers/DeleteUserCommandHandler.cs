using MediatR;
using NuIeee.Application.Features.Users.Commands;
using NuIeee.Application.Interfaces;

namespace NuIeee.Application.Features.Users.Handlers;

public class DeleteUserCommandHandler(IUserManagementRepository _userManagementRepository) :  IRequestHandler<DeleteUserCommand>
{
    public async Task Handle(DeleteUserCommand request, CancellationToken cancellationToken)
    {
        await _userManagementRepository.DeleteUserAsync(request.UserId);
    }
}