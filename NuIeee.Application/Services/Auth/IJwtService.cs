using NuIeee.Domain.Entities;

namespace NuIeee.Application.Services.Auth;

public interface IJwtService
{
    Task<string> GenerateTokenAsync(ApplicationUser user);
}
