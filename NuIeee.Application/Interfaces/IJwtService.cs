using NuIeee.Domain.Entities;

namespace NuIeee.Application.Interfaces;

public interface IJwtService
{
    string GenerateToken(ApplicationUser user);
}
