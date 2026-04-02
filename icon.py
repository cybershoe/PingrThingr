from AppKit import NSImage, NSColor, NSMakeRect, NSSize, NSString, NSFont, NSForegroundColorAttributeName, NSFontAttributeName, NSAppearance
from Foundation import NSUserDefaults



def status_text(latency = 0.0, loss = 0.0):
    size = NSSize(40, 20)
    image = NSImage.alloc().initWithSize_(size)
    
    image.lockFocus()
    
    # Determine text color based on system appearance
    defaults = NSUserDefaults.standardUserDefaults()
    dark_mode = defaults.stringForKey_("AppleInterfaceStyle") == "Dark"
    
    if dark_mode:
        theme_color = NSColor.whiteColor()
    else:
        theme_color = NSColor.blackColor()
    
    # Set up font and attributes
    normalFont = NSFont.systemFontOfSize_(9)
    boldFont = NSFont.boldSystemFontOfSize_(9)

    match latency:
        case l if l < 1:
            text_color = theme_color
            font = normalFont
        case l if l < 2:
            text_color = NSColor.blackColor()
            font = boldFont

            NSColor.yellowColor().set()
            rect = NSMakeRect(0, 10, 40, 10)
            NSColor.yellowColor().drawSwatchInRect_(rect)
        case l if l < 1000:
            text_color = NSColor.blackColor()
            font = boldFont
            NSColor.orangeColor().set()
            rect = NSMakeRect(0, 10, 40, 10)
            NSColor.orangeColor().drawSwatchInRect_(rect)
        case _:
            text_color = NSColor.whiteColor()
            font = boldFont
            NSColor.redColor().set()
            rect = NSMakeRect(0, 10, 40, 10)
            NSColor.redColor().drawSwatchInRect_(rect)


    attributes = {NSForegroundColorAttributeName: text_color, NSFontAttributeName: font}
    
    # Format and draw latency text in top half (right-justified)
    latency_text = NSString.stringWithString_(f"{latency:.0f} ms")
    latency_size = latency_text.sizeWithAttributes_(attributes)
    latency_x = size.width - latency_size.width - 2
    latency_text.drawAtPoint_withAttributes_((latency_x, 10), attributes)
    
    loss_text = NSString.stringWithString_(f"{loss:.0f} %")
    loss_attributes = {NSForegroundColorAttributeName: NSColor.systemRedColor(), NSFontAttributeName: font}

    loss_size = loss_text.sizeWithAttributes_(loss_attributes)
    loss_x = size.width - loss_size.width - 6
    loss_text.drawAtPoint_withAttributes_((loss_x, 0), loss_attributes)

    
    image.unlockFocus()
    return image

def paused_icon():
    # Create SF Symbol image
    symbol_image = NSImage.imageWithSystemSymbolName_accessibilityDescription_("pause.circle", "Paused")
    
    # Create a new 20x20 image
    size = NSSize(20, 20)
    resized_image = NSImage.alloc().initWithSize_(size)
    
    resized_image.lockFocus()
    
    # Draw the symbol image scaled to fit the 20x20 size
    symbol_image.drawInRect_(NSMakeRect(0, 0, 20, 20))
    
    resized_image.unlockFocus()
    resized_image.setTemplate_(True)
    return resized_image