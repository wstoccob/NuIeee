using Microsoft.AspNetCore.Identity;
using NuIeee.Application.DTOs.Auth;
using NuIeee.Domain.Entities;

namespace NuIeee.Application.Services.Auth;

public class AuthService : IAuthService
{
    private readonly UserManager<ApplicationUser> _userManager;
    private readonly SignInManager<ApplicationUser> _signInManager;
    private readonly IJwtService _jwtService;

    public AuthService(
        UserManager<ApplicationUser> userManager,
        SignInManager<ApplicationUser> signInManager,
        IJwtService jwtService)
    {
        _userManager = userManager;
        _signInManager = signInManager;
        _jwtService = jwtService;
    }

    public async Task<string> LoginAsync(LoginDto loginDto)
    {
        var user = await _userManager.FindByNameAsync(loginDto.Username);

        if (user == null)
        {
            throw new InvalidOperationException("User not found");
        }

        var result = await _signInManager.CheckPasswordSignInAsync(user, loginDto.Password, false);

        if (!result.Succeeded)
        {
            throw new InvalidOperationException("Invalid username or password");
        }

        return await _jwtService.GenerateTokenAsync(user);
    }

    public async Task<Guid> RegisterAsync(string username, string password)
    {
        var user = new ApplicationUser
        {
            UserName = username
        };

        var result = await _userManager.CreateAsync(user, password);

        if (!result.Succeeded)
        {
            var errors = string.Join("; ", result.Errors.Select(e => e.Description));
            throw new InvalidOperationException($"User registration failed: {errors}");
        }

        return user.Id;
    }
}
