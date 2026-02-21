using NuIeee.Application.DTOs.Auth;

namespace NuIeee.Application.Services.Auth;

public interface IAuthService
{
    Task<string> LoginAsync(LoginDto loginDto);
    Task<Guid> RegisterAsync(string username, string password);
}
