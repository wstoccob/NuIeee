using NuIeee.Application.DTOs.Identity;
using NuIeee.Domain.Entities;

namespace NuIeee.Application.Interfaces;

public interface IUserManagementRepository
{
    Task<List<UserDto>> GetAllUsersAsync();
    Task<Guid> CreateUserAsync(string username, string fullname, string password, string role);
    Task<bool> DeleteUserAsync(Guid userId);
    Task<UserDto?> GetUserByIdAsync(Guid userId);
}