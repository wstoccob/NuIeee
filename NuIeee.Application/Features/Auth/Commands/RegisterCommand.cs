using MediatR;

namespace NuIeee.Application.Features.Auth.Commands;

public record RegisterCommand(string Username, string Password) : IRequest<Guid>;