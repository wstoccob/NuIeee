using MediatR;
using Microsoft.AspNetCore.Identity;
using NuIeee.Application.Features.Auth.Queries;
using NuIeee.Application.Interfaces;
using NuIeee.Domain.Entities;

namespace NuIeee.Application.Features.Auth.Handlers;

public class LoginQueryHandler : IRequestHandler<LoginQuery, string>
{
    private readonly UserManager<ApplicationUser> _userManager;
    private readonly SignInManager<ApplicationUser> _signInManager;
    private readonly IJwtService _jwtService;

    public LoginQueryHandler(
        UserManager<ApplicationUser> userManager,
        SignInManager<ApplicationUser> signInManager,
        IJwtService jwtService)
    {
        _userManager = userManager;
        _signInManager = signInManager;
        _jwtService = jwtService;
    }

    public async Task<string> Handle(LoginQuery request, CancellationToken cancellationToken)
    {
        var user = await _userManager.FindByNameAsync(request.LoginDto.Username);

        if (user == null)
        {
            throw new InvalidOperationException("User not found");
        }

        var result = await _signInManager.CheckPasswordSignInAsync(user, request.LoginDto.Password, false);

        if (!result.Succeeded)
        {
            throw new InvalidOperationException("Invalid username or password");
        }

        return await _jwtService.GenerateTokenAsync(user);
    }
}