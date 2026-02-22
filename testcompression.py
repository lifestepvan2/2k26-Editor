from nba2k_editor.assets.logo_patcher.iff_utils import unpack_iff, read_txtr, find_texture_binary_path
from nba2k_editor.assets.logo_patcher.tld_utils import diagnose_compression
tmp = unpack_iff(r"logo024.iff")
meta = read_txtr(tmp)
bin_path, kind = find_texture_binary_path(tmp)
print(f"Binary type: {kind}  ({bin_path.name})")
diagnose_compression(bin_path, meta)
