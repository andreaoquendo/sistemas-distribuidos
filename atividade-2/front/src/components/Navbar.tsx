import { Link } from "react-router-dom";
import styled from "styled-components";

const Nav = styled.nav`
  padding: 16px;
  background-color: #001f3f;
  display: flex;
  gap: 16px;
`;

const NavLink = styled(Link)`
  color: white;
  text-decoration: none;

  &:hover {
    text-decoration: underline;
  }
`;

export function Navbar() {
  return (
    <Nav>
      <NavLink to="/">Consulta</NavLink>
      <NavLink to="/reserva">Reserva</NavLink>
      <NavLink to="/status">Status</NavLink>
      <NavLink to="/promocoes">Promoções</NavLink>
      <NavLink to="/admin">Admin</NavLink>
    </Nav>
  );
}
