import edu.lab.rev.course04.LicenseCheck;

// Arbitration driver: calls the real compiled LicenseCheck bytecode
// from the APK build output. Used when Python and PowerShell
// implementations disagree.
public class Verify {

    static void gen(int uid, int days, int flags) {
        String k = LicenseCheck.INSTANCE.encodeKey(uid, days, flags);
        boolean ok = LicenseCheck.INSTANCE.isValidKey(k);
        LicenseCheck.License lic = LicenseCheck.INSTANCE.parseKey(k);
        System.out.println("ENC " + uid + "," + days + "," + flags
                + " -> " + k
                + " | valid=" + ok
                + " | uid=" + (lic == null ? "-" : lic.getUserId())
                + " days=" + (lic == null ? "-" : lic.getExpiryDays())
                + " flags=" + (lic == null ? "-" : lic.getFlags()));
    }

    static void chk(String k) {
        boolean ok = LicenseCheck.INSTANCE.isValidKey(k);
        LicenseCheck.License lic = LicenseCheck.INSTANCE.parseKey(k);
        System.out.println("CHK " + k + " -> valid=" + ok
                + " | " + (lic == null ? "null" :
                  "uid=" + lic.getUserId() + " days=" + lic.getExpiryDays() + " flags=" + lic.getFlags()));
    }

    public static void main(String[] args) {
        gen(1, 365, 5);
        gen(7, 30, 4);
        gen(4095, 2047, 15);

        chk("LAB4-AAAT-PXLW");
        chk("LAB4-AADS-D3GC");
        chk("LAB4-B99Z-998A");

        chk("LAB4-AAAT-PXRE");
        chk("LAB4-AADS-D3DU");
        chk("LAB4-B99Z-995S");

        gen(4242, 365, 5);
        chk("LAB4-AAAA-AAAA");
    }
}
