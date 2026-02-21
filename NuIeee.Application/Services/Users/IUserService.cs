using NuIeee.Application.DTOs.Identity;

namespace NuIeee.Application.Services.Users;

public interface IUserService
{
    Task<List<UserDto>> GetAllUsersAsync();
    Task<UserDto> GetUserByIdAsync(Guid userId);
    Task<Guid> CreateUserAsync(string username, string fullname, string password, string role);
    Task DeleteUserAsync(Guid userId);
}
