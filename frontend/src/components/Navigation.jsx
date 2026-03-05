import { useState } from "react";
import { NavLink } from "react-router-dom";

function Navigation() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="nav" aria-label="Main">
      <button className="hamburger" onClick={() => setOpen((v) => !v)}>
        ☰
      </button>

      {open && (
        <div className="nav-menu">
          <NavLink to="/" className="nav-link">Home</NavLink>
          <NavLink to="/past-uploads" className="nav-link">Past Uploads</NavLink>
          <NavLink to="/inventory" className="nav-link">Inventory</NavLink>
        </div>
      )}
    </nav>
  );
}

export default Navigation;