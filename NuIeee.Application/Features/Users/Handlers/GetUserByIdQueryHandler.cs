using MediatR;
using NuIeee.Application.DTOs.Identity;
using NuIeee.Application.Features.Users.Queries;
using NuIeee.Application.Interfaces;

namespace NuIeee.Application.Features.Users.Handlers;

public class GetUserByIdQueryHandler(IUserManagementRepository _userManagementRepository) : IRequestHandler<GetUserByIdQuery, UserDto>
{
    public async Task<UserDto> Handle(GetUserByIdQuery request, CancellationToken cancellationToken)
    {
        return await _userManagementRepository.GetUserByIdAsync(request.UserId);
    }
}