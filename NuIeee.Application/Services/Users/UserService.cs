using NuIeee.Application.DTOs.Identity;
using NuIeee.Application.Interfaces;

namespace NuIeee.Application.Services.Users;

public class UserService : IUserService
{
    private readonly IUserManagementRepository _userManagementRepository;

    public UserService(IUserManagementRepository userManagementRepository)
    {
        _userManagementRepository = userManagementRepository;
    }

    public async Task<List<UserDto>> GetAllUsersAsync()
    {
        return await _userManagementRepository.GetAllUsersAsync();
    }

    public async Task<UserDto> GetUserByIdAsync(Guid userId)
    {
        return await _userManagementRepository.GetUserByIdAsync(userId);
    }

    public async Task<Guid> CreateUserAsync(string username, string fullname, string password, string role)
    {
        var id = await _userManagementRepository.CreateUserAsync(username, fullname, password, role);
        return id;
    }

    public async Task DeleteUserAsync(Guid userId)
    {
        await _userManagementRepository.DeleteUserAsync(userId);
    }
}
