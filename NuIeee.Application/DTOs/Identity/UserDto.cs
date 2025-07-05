using System.Runtime;

namespace NuIeee.Application.DTOs.Identity;

public class UserDto
{
    public string Id { get; set; }
    public string Username { get; set; }
    public string Fullname { get; set; }
    public List<string> Roles { get; set; }
}