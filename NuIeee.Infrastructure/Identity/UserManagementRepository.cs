using Microsoft.AspNetCore.Identity;
using Microsoft.EntityFrameworkCore;
using NuIeee.Application.DTOs.Identity;
using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;

namespace NuIeee.Infrastructure.Identity;

public class UserManagementRepository :  IUserManagementRepository
{
    private readonly UserManager<ApplicationUser> _userManager;
    private readonly RoleManager<IdentityRole<Guid>> _roleManager;
    
    public UserManagementRepository(UserManager<ApplicationUser> userManager, RoleManager<IdentityRole<Guid>> roleManager)
    {
        _userManager = userManager;
        _roleManager = roleManager;
    }
    
    public async Task<List<UserDto>> GetAllUsersAsync()
    {
        var users = await _userManager.Users.ToListAsync();
        var result = new List<UserDto>();

        foreach (var user in users)
        {
            IList<string> roles = await _userManager.GetRolesAsync(user);
            
            result.Add(new UserDto
            {
                Id = user.Id.ToString(),
                Username = user.UserName,
                Fullname = user.FullName,
                Roles = roles.Distinct().ToList(),
            });
        }

        return result;
    }

    public async Task<Guid> CreateUserAsync(string username, string fullname, string password, string role)
    {
        if (!await _roleManager.RoleExistsAsync(role))
        {
            throw new InvalidOperationException($"Role {role} not found");
        }

        var user = new ApplicationUser { UserName = username, FullName = fullname};
        var result = await _userManager.CreateAsync(user, password);

        if (!result.Succeeded)
        {
            throw new InvalidOperationException($"Could not create user with username - {username}");
        }

        await _userManager.AddToRoleAsync(user, role);
        return user.Id;
    }

    public async Task<bool> DeleteUserAsync(Guid userId)
    {
        var user = await _userManager.FindByIdAsync(userId.ToString());
        if (user == null)
        {
            throw new InvalidOperationException($"User with id {userId} not found");
        }

        var roles = await _userManager.GetRolesAsync(user);
        if (roles.Contains("SuperAdmin"))
        {
            throw new InvalidOperationException("Cannot delete SuperAdmins");
        }

        var result = await _userManager.DeleteAsync(user);
        return result.Succeeded;
    }

    public async Task<UserDto?> GetUserByIdAsync(Guid userId)
    {
        var user = await _userManager.FindByIdAsync(userId.ToString());

        if (user == null)
        {
            throw new InvalidOperationException($"User with id {userId} not found");
        }
        
        var roles = await _userManager.GetRolesAsync(user);
        var userDto = new UserDto
        {
            Id = user.Id.ToString(),
            Username = user.UserName,
            Fullname = user.FullName,
            Roles = roles.Distinct().ToList(),
        };
        
        return userDto;
    }
}