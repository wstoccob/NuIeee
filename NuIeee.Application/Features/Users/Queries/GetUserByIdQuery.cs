using MediatR;
using NuIeee.Application.DTOs.Identity;

namespace NuIeee.Application.Features.Users.Queries;

public record GetUserByIdQuery(Guid UserId) : IRequest<UserDto>;