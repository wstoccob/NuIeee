using MediatR;
using NuIeee.Application.Features.Users.Commands;
using NuIeee.Application.Interfaces;

namespace NuIeee.Application.Features.Users.Handlers;

public class CreateUserCommandHandler(IUserManagementRepository _userManagementRepository) : IRequestHandler<CreateUserCommand, Guid>
{
    public async Task<Guid> Handle(CreateUserCommand request, CancellationToken cancellationToken)
    {
        var id = await _userManagementRepository.CreateUserAsync(request.Username, request.Password, request.Role);

        return id;
    }
}