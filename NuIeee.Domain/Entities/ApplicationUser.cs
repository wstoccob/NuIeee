using Microsoft.AspNetCore.Identity;

namespace NuIeee.Domain.Entities;

public class ApplicationUser : IdentityUser<Guid>
{
    public string FullName { get; set; } = string.Empty;
}
