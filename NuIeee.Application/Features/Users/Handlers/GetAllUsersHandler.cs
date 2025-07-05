using MediatR;
using NuIeee.Application.DTOs.Identity;
using NuIeee.Application.Features.Users.Queries;
using NuIeee.Application.Interfaces;

namespace NuIeee.Application.Features.Users.Handlers;

public class GetAllUsersHandler : IRequestHandler<GetAllUsersQuery, List<UserDto>>
{
    public readonly IUserManagementRepository _userManagementRepository;

    public GetAllUsersHandler(IUserManagementRepository userManagementRepository)
    {
        _userManagementRepository = userManagementRepository;
    }
    
    public async Task<List<UserDto>> Handle(GetAllUsersQuery request, CancellationToken cancellationToken)
    {
        var result = await _userManagementRepository.GetAllUsersAsync();
        
        return  result;
    }
}