using NuIeee.Domain.Entities;

namespace NuIeee.Application.Interfaces;

public interface IJwtService
{
    Task<string> GenerateTokenAsync(ApplicationUser user);
}
