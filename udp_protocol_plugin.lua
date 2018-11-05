--------------------------------------------------------------------------------
---- Wireshark Protocol Plugin Base On UDP
--------------------------------------------------------------------------------
local udp_table = DissectorTable.get("udp.port")
local my_proto = Proto("udp-sample", "udp sample protocol", "udp sample protocol")
local my_port = 99999

---- Define many fields
local version_field = ProtoField.uint16("Version", "Version", base.DEC)
local id_field = ProtoField.uint32("ID", "ID", base.DEC)
local string_field = ProtoField.string("Buffer", "Buffer")

my_proto.fields = {version_field, id_field, string_field}

function my_proto.dissector(buffer, pinfo, tree)
    pinfo.cols.protocol:set("udp-sample")

    local len = buffer:len()
    local my_proto_tree = tree:add(my_proto, buffer(0, len), "udp sample protocol")
    local offset = 0

    my_proto_tree:add(version_field, buffer(offset, 2))
    offset = offset + 2

    my_proto_tree:add(id_field, buffer(offset, 4))
    offset = offset + 4

    my_proto_tree:add(string_field, buffer(offset, 1024))
end

udp_table:add(my_port, my_proto)
