from py2opsin import py2opsin as opsin


def name_to_format(name: str | list, out_format: str = "SMILES") -> str | list:
    """
    Input simplifier for py2opsin.

    Use list of names for batch processing as
    there is a performance boost.

    Parameters
    ----------
    name : str
        DESCRIPTION.
    out_format : str, optional
        DESCRIPTION. The default is "SMILES".

    Returns
    -------
    str
        DESCRIPTION.

    """
    return opsin(
        chemical_name=name,
        output_format=out_format,
        allow_acid=False,
        allow_radicals=True,
        allow_bad_stereo=False,
        wildcard_radicals=False)
